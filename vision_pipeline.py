#!/usr/bin/env python3
"""
Pipeline imagen->codigo Voynich (Frente B: plantas herbales discriminantes).
Vision-LLM local via Ollama. Autocontenido y RESUMIBLE.
Mapeo folio<->scan DETERMINISTA (herbal temprano f1-f57): folio=(scan+1)//2, recto si scan impar.
(Verificado: scan39=f20r, scan4=f2v). El modelo NO lee el folio (poco fiable); solo describe la planta.
"""
import os, re, json, base64, urllib.request, collections, argparse, math, time, subprocess

HERE=os.path.dirname(os.path.abspath(__file__))
CACHE=os.path.join(HERE,"scans"); os.makedirs(CACHE,exist_ok=True)
ANNOT=os.path.join(HERE,"annotations.jsonl")
OLLAMA="http://localhost:11434/api/generate"

PROMPT=("This is one page of a medieval herbal manuscript showing a single plant. "
        "Describe the plant's morphology. Reply ONLY with JSON, no prose: "
        '{"root_form":"taproot|branching|bulbous|fibrous|tuber|none",'
        '"leaf_form":"pinnate|simple|lobed|serrated|needle|none",'
        '"leaf_arrangement":"basal|opposite|alternate|whorled|na",'
        '"flower":"present|absent",'
        '"dominant_color":"green|brown|red|blue|mixed",'
        '"n_leaflets":<int or null>}')

def scan_to_folio(n):
    folio=(n+1)//2
    return f"f{folio}{'r' if n%2==1 else 'v'}"

def discriminating_words(path=os.path.join(HERE,"voy_lsi.txt"), lo=4, hi=8):
    sec=None; folw=collections.defaultdict(set)
    for raw in open(path,encoding="latin-1"):
        if raw.startswith("<") and "$I=" in raw:
            m=re.search(r"\$I=([A-Z])",raw); sec=m.group(1) if m else None
        m=re.match(r"<(f[0-9]+[rv][0-9]?)\.[0-9]+,.([A-Za-z][A-Za-z0-9]*);H>\s*(.*)",raw)
        if not m or sec!="H": continue
        fol,typ,bd=m.groups()
        if typ[0]!="P": continue
        for w in re.split(r"[.,]",bd.strip().rstrip("<->").strip()):
            w=w.replace("!","").replace("%","").replace("$","")
            if w and "?" not in w and "*" not in w and len(w)>=4: folw[fol].add(w)
    wf=collections.Counter()
    for ws in folw.values():
        for w in ws: wf[w]+=1
    return {w:sorted(f for f in folw if w in folw[f]) for w,c in wf.items() if lo<=c<=hi}

def get_scan(n):
    p=os.path.join(CACHE,f"{n:03d}.jpg")
    if os.path.exists(p) and os.path.getsize(p)>0: return p
    tmp=f"/tmp/vp_{n}.jpg"
    urllib.request.urlretrieve(f"https://archive.org/download/voynich/{n:03d}.jpg",tmp)
    subprocess.run(["sips","-Z","1500",tmp,"--out",p],capture_output=True)
    try: os.remove(tmp)
    except OSError: pass
    return p

def annotate(model,img):
    b64=base64.b64encode(open(img,"rb").read()).decode()
    body=json.dumps({"model":model,"prompt":PROMPT,"images":[b64],"stream":False,
                     "format":"json","options":{"temperature":0}}).encode()
    req=urllib.request.Request(OLLAMA,data=body,headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=600) as r: out=json.load(r)
    try: return json.loads(out.get("response","{}"))
    except Exception: return {"raw":out.get("response","")[:200]}

def done_scans():
    s=set()
    if os.path.exists(ANNOT):
        for line in open(ANNOT):
            try: s.add(json.loads(line)["scan"])
            except Exception: pass
    return s

def cross():
    disc=discriminating_words()
    fol2=collections.OrderedDict()
    for line in open(ANNOT):
        try: r=json.loads(line)
        except Exception: continue
        f=r.get("det_folio")
        if f: fol2[f]=r
    print(f"\n=== CRUCE figura->codigo ===\nfolios anotados: {len(fol2)}")
    # baseline: distribucion de cada rasgo sobre TODAS las plantas
    def basedist(key):
        c=collections.Counter(v.get(key) for v in fol2.values() if v.get(key) not in (None,"none","na"))
        t=sum(c.values()); return c, t
    for key in ("root_form","leaf_form"):
        c,t=basedist(key)
        print(f"baseline {key}: "+", ".join(f"{k}={round(100*v/t)}%" for k,v in c.most_common()))
    # por palabra discriminante: rasgo modal + LIFT sobre baseline
    print("\npalabra    | folios | rasgo compartido (frac) | lift vs baseline")
    rows=[]
    for key in ("root_form","leaf_form"):
        base,_=basedist(key); bt=sum(base.values())
        for w,fols in disc.items():
            vals=[fol2[f].get(key) for f in fols if f in fol2 and fol2[f].get(key) not in (None,"none","na")]
            if len(vals)<3: continue
            cc=collections.Counter(vals); top,n=cc.most_common(1)[0]
            frac=n/len(vals); basefrac=base.get(top,0)/bt if bt else 0
            lift=frac/basefrac if basefrac else 0
            rows.append((lift,frac,len(vals),w,key,top,n))
    rows.sort(reverse=True)
    for lift,frac,nv,w,key,top,n in rows[:20]:
        flag="  <== FUERTE" if (frac>=0.7 and lift>=1.5 and nv>=3) else ""
        print(f"{w:10} | {nv:2} pl | {key[:4]}={top}({n}/{nv},{frac*100:.0f}%) | lift {lift:.2f}x{flag}")
    strong=[r for r in rows if r[1]>=0.7 and r[0]>=1.5 and r[2]>=3]
    print(f"\nSEÑALES FUERTES (>=70% comparten un rasgo, >=1.5x baseline): {len(strong)}")
    print("-> si hay varias, es candidato a PUENTE figura->codigo. Si ~0, el codigo no mapea a parte fisica visible (=> esencia/abstracto).")

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--model",default="qwen2.5vl:7b")
    ap.add_argument("--scans",default="3-116")
    ap.add_argument("--cross-only",action="store_true")
    a=ap.parse_args()
    if a.cross_only: cross(); raise SystemExit
    lo,hi=map(int,a.scans.split("-")); already=done_scans()
    n_done=0
    with open(ANNOT,"a") as out:
        for n in range(lo,hi+1):
            if n in already: continue
            try:
                t0=time.time(); res=annotate(a.model,get_scan(n))
                res["scan"]=n; res["det_folio"]=scan_to_folio(n)
                out.write(json.dumps(res)+"\n"); out.flush(); n_done+=1
                print(f"scan {n:3d} ({res['det_folio']:6}) root={res.get('root_form')} leaf={res.get('leaf_form')} [{time.time()-t0:.0f}s]",flush=True)
            except Exception as e:
                print(f"scan {n:3d} ERROR: {e}",flush=True)
    print(f"\nanotadas {n_done} nuevas plantas.")
    cross()
