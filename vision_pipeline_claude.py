#!/usr/bin/env python3
"""
Pipeline imagen->codigo Voynich con Claude API (vision frontera). EXTRACCION MAXIMA:
un solo call por planta -> record rico (raiz/hoja/tallo/flor/fruto/porte/composicion/ID/colores).
Habilita 4 analisis: cruce figura->codigo, plantas compuestas, cribs por ID, correlaciones.

Key: en ~/voynich-poc/.anthropic_key (NO en el codigo). Modelo configurable.
Uso:  python3 vision_pipeline_claude.py --model claude-sonnet-5 --scans 3-116
      python3 vision_pipeline_claude.py --cross-only
"""
import os, re, json, base64, urllib.request, collections, argparse, math, time, subprocess, pathlib

HERE=os.path.dirname(os.path.abspath(__file__))
CACHE=os.path.join(HERE,"scans"); os.makedirs(CACHE,exist_ok=True)
ANNOT=os.path.join(HERE,"annotations_claude.jsonl")
API="https://api.anthropic.com/v1/messages"

def api_key():
    f=pathlib.Path(HERE)/".anthropic_key"
    if f.exists(): return f.read_text().strip()
    k=os.environ.get("ANTHROPIC_API_KEY")
    if k: return k.strip()
    raise SystemExit("Falta la key: echo 'sk-ant-...' > ~/voynich-poc/.anthropic_key")

PROMPT=(
"You are a botanist examining ONE page of the Voynich herbal manuscript (a single stylised plant). "
"Return ONLY strict JSON with these fields (use the allowed values; use \"none\"/null if not visible):\n"
'{\n'
'"root_form":"taproot|tuber|rhizome|bulb|corm|fibrous|napiform|branching|adventitious|none",\n'
'"root_color":"brown|red|tan|green|white|other|none",\n'
'"n_roots":<int or null>,\n'
'"stem_count":"single|few|many|none",\n'
'"leaf_form":"pinnate|bipinnate|palmate|ovate|lanceolate|cordate|linear|lobed|serrated|needle|none",\n'
'"leaf_arrangement":"basal_rosette|opposite|alternate|whorled|na",\n'
'"n_leaves":<int or null>,\n'
'"leaf_color":"green|blue|brown|mixed|other|none",\n'
'"flower":"present|absent",\n'
'"flower_color":"red|blue|yellow|white|green|mixed|none",\n'
'"flower_form":"bell|star|cluster|spike|umbel|composite|other|none",\n'
'"fruit":"pod|berry|capsule|none",\n'
'"habit":"herb|shrub|vine|aquatic|treelike",\n'
'"composite_score":<1-5 how CHIMERIC: 1=anatomically coherent real plant, 5=mismatched parts fused>,\n'
'"composite_note":"<short: which parts look mismatched, or coherent>",\n'
'"resembles_plant":"<real plant name or null>",\n'
'"id_confidence":"high|medium|low|none",\n'
'"dominant_colors":["green","brown","red","blue","yellow"],\n'
'"n_distinct_parts":<int>,\n'
'"distinctive":"<one short phrase>"\n'
'}'
)

def scan_to_folio(n):
    folio=(n+1)//2
    return f"f{folio}{'r' if n%2==1 else 'v'}"

def get_scan(n):
    p=os.path.join(CACHE,f"{n:03d}.jpg")
    if os.path.exists(p) and os.path.getsize(p)>0: return p
    tmp=f"/tmp/vpc_{n}.jpg"
    urllib.request.urlretrieve(f"https://archive.org/download/voynich/{n:03d}.jpg",tmp)
    subprocess.run(["sips","-Z","1568",tmp,"--out",p],capture_output=True)
    try: os.remove(tmp)
    except OSError: pass
    return p

def annotate(model,key,img):
    b64=base64.b64encode(open(img,"rb").read()).decode()
    body=json.dumps({"model":model,"max_tokens":700,
        "messages":[{"role":"user","content":[
            {"type":"image","source":{"type":"base64","media_type":"image/jpeg","data":b64}},
            {"type":"text","text":PROMPT}]}]}).encode()
    req=urllib.request.Request(API,data=body,headers={
        "x-api-key":key,"anthropic-version":"2023-06-01","content-type":"application/json"})
    with urllib.request.urlopen(req,timeout=120) as r: out=json.load(r)
    txt="".join(b.get("text","") for b in out.get("content",[]) if b.get("type")=="text")
    usage=out.get("usage",{})
    m=re.search(r"\{.*\}",txt,re.S)
    rec=json.loads(m.group(0)) if m else {"raw":txt[:200]}
    rec["_in"]=usage.get("input_tokens"); rec["_out"]=usage.get("output_tokens")
    return rec

def done_scans():
    s=set()
    if os.path.exists(ANNOT):
        for line in open(ANNOT):
            try: s.add(json.loads(line)["scan"])
            except Exception: pass
    return s

def discriminating_words(lo=4,hi=8):
    sec=None; folw=collections.defaultdict(set)
    for raw in open(os.path.join(HERE,"voy_lsi.txt"),encoding="latin-1"):
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

def cross():
    import random; random.seed(0)
    fol2={}
    for line in open(ANNOT):
        try: d=json.loads(line)
        except Exception: continue
        f=d.get("det_folio")
        if f: fol2[f]=d
    print(f"\n=== CRUCE (Claude) — {len(fol2)} plantas ===")
    KEYS=["root_form","leaf_form","flower_form","habit","fruit","leaf_arrangement"]
    for k in KEYS:
        c=collections.Counter(v.get(k) for v in fol2.values() if v.get(k) not in (None,"none","na"))
        if c: print(f"baseline {k}: "+", ".join(f"{a}={round(100*b/sum(c.values()))}%" for a,b in c.most_common(5)))
    disc=discriminating_words()
    def count_strong(fm):
        s=0
        for k in KEYS:
            b=collections.Counter(v.get(k) for v in fm.values() if v.get(k) not in (None,"none","na")); bt=sum(b.values()) or 1
            for w,fols in disc.items():
                vals=[fm[f].get(k) for f in fols if f in fm and fm[f].get(k) not in (None,"none","na")]
                if len(vals)<4: continue
                cc=collections.Counter(vals); top,n=cc.most_common(1)[0]; frac=n/len(vals)
                lift=frac/(b.get(top,0)/bt) if b.get(top,0) else 0
                if frac>=0.75 and lift>=1.6: s+=1
        return s
    real=count_strong(fol2)
    keys=list(fol2.keys()); nulls=[]
    for _ in range(40):
        vals=[dict(fol2[k]) for k in keys]; random.shuffle(vals)
        nulls.append(count_strong({k:vals[i] for i,k in enumerate(keys)}))
    mx=max(nulls); mean=sum(nulls)/len(nulls)
    print(f"\nseñales fuertes REAL={real}  NULO barajado={mean:.0f} (max {mx})")
    print("VEREDICTO:", "ARTEFACTO (real<=nulo)" if real<=mx else f"POSIBLE SEÑAL (real excede nulo por {real-mx})")
    # extras: composicion + IDs confiables
    comp=[v.get("composite_score") for v in fol2.values() if isinstance(v.get("composite_score"),(int,float))]
    if comp: print(f"\n[compuestas] score medio {sum(comp)/len(comp):.1f}/5  |  quiméricas(>=4): {sum(1 for x in comp if x>=4)}/{len(comp)}")
    ids=[(v.get("det_folio"),v.get("resembles_plant")) for v in fol2.values() if v.get("id_confidence")=="high"]
    print(f"[IDs confianza alta] {len(ids)}: "+", ".join(f"{f}:{p}" for f,p in ids[:12]))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--model",default="claude-sonnet-5")
    ap.add_argument("--scans",default="3-116")
    ap.add_argument("--cross-only",action="store_true")
    a=ap.parse_args()
    if a.cross_only: cross(); raise SystemExit
    key=api_key(); lo,hi=map(int,a.scans.split("-")); already=done_scans()
    tin=tout=0
    with open(ANNOT,"a") as out:
        for n in range(lo,hi+1):
            if n in already: continue
            try:
                t0=time.time(); r=annotate(a.model,key,get_scan(n))
                r["scan"]=n; r["det_folio"]=scan_to_folio(n)
                out.write(json.dumps(r)+"\n"); out.flush()
                tin+=r.get("_in") or 0; tout+=r.get("_out") or 0
                print(f"scan {n:3d} ({r['det_folio']:6}) root={r.get('root_form')} leaf={r.get('leaf_form')} comp={r.get('composite_score')} id={r.get('resembles_plant')}({r.get('id_confidence')}) [{time.time()-t0:.0f}s]",flush=True)
            except Exception as e:
                print(f"scan {n:3d} ERROR: {e}",flush=True)
    # costo aprox (Sonnet ~$3/M in, $15/M out; ajustar por modelo)
    print(f"\ntokens: in={tin:,} out={tout:,}  costo aprox Sonnet: ${tin/1e6*3 + tout/1e6*15:.2f}")
    cross()
