#!/usr/bin/env python3
"""
Test de ETIQUETAS v2 — RIGOR de emparejamiento.
Mejoras sobre v1:
  (a) se le DICE a la visión el nº exacto N de objetos rotulados del folio (de la transliteración)
      y se le piden COORDENADAS normalizadas [x,y] de cada uno.
  (b) emparejamiento por ORDEN DE LECTURA 2D: etiquetas de la transliteración ordenadas por (línea,idx)
      vs objetos ordenados por (banda-fila y, luego x) — mucho más robusto al desfase ±1 de v1.
  (c) AGREGA sub-paneles de foldout (f102v2->f102v, etc.) para recuperar folios que salían con 0.
  (d) cruce con rasgo FINO (part y part+color) + permutación + out-of-sample.
Uso: python3 label_crib_v2.py --model claude-sonnet-5           (anota+cruza)
     python3 label_crib_v2.py --cross-only
"""
import os, re, json, base64, argparse, collections, math, random, subprocess, urllib.request, pathlib
random.seed(0)
HERE=os.path.dirname(os.path.abspath(__file__))
OBJ=os.path.join(HERE,"label_objects_v2.json")
API="https://api.anthropic.com/v1/messages"

# scans verificados por nº de esquina (foldout farmacéutico f99-f102)
SCAN={"f99r":175,"f99v":176,"f100r":177,"f100v":178,"f101r":179,"f101v":180,"f102r":181,"f102v":182}

def api_key():
    f=pathlib.Path(HERE)/".anthropic_key"
    if f.exists(): return f.read_text().strip()
    raise SystemExit("Falta ~/voynich-poc/.anthropic_key")

PRE=["qok","qot","qol","qo","ok","ot","op","o","cth","ckh","ch","sh","d","s","y","l","r","k","t","p","f","a"]
SUF=["aiin","aiiin","ain","iin","eedy","eeey","eey","eody","edy","ody","ey","dy","ol","or","al","ar","am","in","y","s","o","d","l","r","n"]
def dec(w):
    core=w;pre="";suf=""
    for p in PRE:
        if core.startswith(p) and len(core)>len(p): pre=p;core=core[len(p):];break
    for s in SUF:
        if core.endswith(s) and len(core)>len(s): suf=s;core=core[:-len(s)];break
    return (pre,core,suf) if pre and suf else None

def base_folio(k):
    m=re.match(r"(f\d+[rv])\d*",k); return m.group(1) if m else k

def load_labels():
    """agrega sub-paneles al folio base, en orden (panel, línea, idx)."""
    raw=json.load(open(os.path.join(HERE,"labels.json")))
    agg=collections.defaultdict(list)
    for k in sorted(raw):
        b=base_folio(k)
        for l in raw[k]:
            agg[b].append({"word":l["word"],"dec":l["dec"],"key":k,"line":l["line"],"idx":l["idx"]})
    for b in agg:
        agg[b].sort(key=lambda l:(l["key"],l["line"],l["idx"]))
    return agg

def get_scan(fol):
    n=SCAN[fol]; p=os.path.join(HERE,"scans",f"{n:03d}.jpg")
    if os.path.exists(p) and os.path.getsize(p)>300000: return p  # exige alta-res
    tmp=f"/tmp/v2_{n}.jpg"
    urllib.request.urlretrieve(f"https://archive.org/download/voynich/{n:03d}.jpg",tmp)
    subprocess.run(["sips","-Z","1800",tmp,"--out",p],capture_output=True)
    try: os.remove(tmp)
    except OSError: pass
    return p

def prompt_for(n):
    return (
    f"This is a PHARMACEUTICAL page of the Voynich manuscript: detached, individually-drawn plant PARTS "
    f"(roots, leaves, flowers, seed-pods), some in decorated apothecary jars, each with a short label. "
    f"There are EXACTLY {n} labelled drawn objects on this page. Ignore the script (unreadable). "
    f"Return them in READING ORDER (top band first, then left-to-right within each band). Return ONLY strict JSON, "
    f"an array of EXACTLY {n} objects:\n"
    '[{"x":<0..1 left→right>,"y":<0..1 top→bottom>,'
    '"part":"root|leaf|flower|seedpod|stem|whole_plant|jar_only|other",'
    '"in_jar":true|false,"color":"green|brown|red|blue|yellow|white|mixed|other"}]')

def annotate(model,key,img,n):
    b64=base64.b64encode(open(img,"rb").read()).decode()
    body=json.dumps({"model":model,"max_tokens":4000,"messages":[{"role":"user","content":[
        {"type":"image","source":{"type":"base64","media_type":"image/jpeg","data":b64}},
        {"type":"text","text":prompt_for(n)}]}]}).encode()
    req=urllib.request.Request(API,data=body,headers={
        "x-api-key":key,"anthropic-version":"2023-06-01","content-type":"application/json"})
    with urllib.request.urlopen(req,timeout=200) as r: out=json.load(r)
    txt="".join(b.get("text","") for b in out.get("content",[]) if b.get("type")=="text")
    m=re.search(r"\[.*\]",txt,re.S)
    arr=json.loads(m.group(0)) if m else []
    return arr, out.get("usage",{})

def reading_order_2d(objs):
    """ordena por bandas de fila (y) y luego x — igual que leería un escriba."""
    if not objs: return objs
    ys=sorted(o.get("y",0.5) for o in objs)
    # banda ~ agrupar y con tolerancia 0.06
    band=[]; cur=[ys[0]]
    for y in ys[1:]:
        if y-cur[-1]<=0.06: cur.append(y)
        else: band.append(cur); cur=[y]
    band.append(cur)
    def bidx(y):
        for i,bb in enumerate(band):
            if bb[0]-1e-9<=y<=bb[-1]+1e-9: return i
        return len(band)
    return sorted(objs,key=lambda o:(bidx(o.get("y",0.5)),o.get("x",0.5)))

def cross():
    LAB=load_labels()
    objs=json.load(open(OBJ)) if os.path.exists(OBJ) else {}
    aligned=[]; report=[]
    for fol,arr in objs.items():
        L=LAB.get(fol,[]); O=reading_order_2d(arr)
        ok=len(L)>0 and abs(len(L)-len(O))<=2
        report.append((fol,len(L),len(O),"pareado" if ok else "descartado"))
        if not ok: continue
        for i in range(min(len(L),len(O))):
            d=L[i]["dec"]
            if d: aligned.append((fol,tuple(d),O[i].get("part"),O[i].get("color")))
    print("=== EMPAREJAMIENTO 2D ===")
    for r in report: print(f"  {r[0]:7} etiquetas={r[1]:3} objetos={r[2]:3} -> {r[3]}")
    print(f"\netiquetas pareadas y descompuestas: {len(aligned)}  de {len(set(a[0] for a in aligned))} folios")
    if len(aligned)<25: print("muestra chica; interpretar con cuidado")

    def run(get_target,tname):
        rows=[(a[0],a[1],get_target(a)) for a in aligned if get_target(a)]
        base=collections.Counter(t for _,_,t in rows); B=sum(base.values())
        print(f"\n### objetivo = {tname}  (n={B})  baseline: "+
              ", ".join(f"{k}={100*v/B:.0f}%" for k,v in base.most_common(6)))
        def strength(rr,comp):
            by=collections.defaultdict(list)
            for _,d,t in rr: by[d[comp]].append(t)
            s=0
            for aff,ts in by.items():
                if len(ts)<4: continue
                c=collections.Counter(ts); top,nn=c.most_common(1)[0]; frac=nn/len(ts)
                lift=frac/(base.get(top,0)/B) if base.get(top,0) else 0
                if frac>=0.6 and lift>=1.6: s+=1
            return s
        for comp,nm in [(0,"PREFIJO"),(2,"SUFIJO")]:
            real=strength(rows,comp)
            nulls=[]; ts=[t for _,_,t in rows]
            for _ in range(1000):
                sh=ts[:]; random.shuffle(sh)
                nulls.append(strength([(rows[i][0],rows[i][1],sh[i]) for i in range(len(rows))],comp))
            mx=max(nulls); mn=sum(nulls)/len(nulls)
            print(f"  [{nm}] REAL={real} nulo={mn:.1f}(max {mx}) -> "+
                  ("POSIBLE CRIB" if real>mx else "NULO"))
        # out-of-sample por sufijo
        fols=sorted(set(r[0] for r in rows)); random.shuffle(fols); half=set(fols[:len(fols)//2])
        tr=collections.defaultdict(collections.Counter)
        for fol,d,t in rows:
            if fol in half: tr[d[2]][t]+=1
        hit=tot=0
        for fol,d,t in rows:
            if fol not in half and tr.get(d[2]):
                tot+=1; hit+= (tr[d[2]].most_common(1)[0][0]==t)
        naive=base.most_common(1)[0][1]/B
        if tot: print(f"  [SUFIJO OOS] acc={hit/tot:.2f} (n={tot}) vs naive={naive:.2f} -> "+
                       ("SUPERA" if hit/tot>naive+0.05 else "no supera"))

    run(lambda a:a[2], "part")
    run(lambda a:(a[2],a[3]) if a[2] and a[3] else None, "part+color")

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--model",default="claude-sonnet-5")
    ap.add_argument("--cross-only",action="store_true")
    a=ap.parse_args()
    if a.cross_only: cross(); raise SystemExit
    LAB=load_labels(); key=api_key()
    out=json.load(open(OBJ)) if os.path.exists(OBJ) else {}
    tin=tout=0
    for fol in [f for f in SCAN if LAB.get(f)]:
        if fol in out: print(f"{fol}: ya anotado"); continue
        N=len(LAB[fol])
        try:
            arr,u=annotate(a.model,key,get_scan(fol),N)
            out[fol]=arr; tin+=u.get("input_tokens") or 0; tout+=u.get("output_tokens") or 0
            print(f"{fol}: pedí {N}, visión devolvió {len(arr)} "+("(ok)" if abs(len(arr)-N)<=2 else "(desalinea)"))
            json.dump(out,open(OBJ,"w"))
        except Exception as e:
            print(f"{fol}: ERROR {e}")
    print(f"\ntokens in={tin:,} out={tout:,} costo ${tin/1e6*3+tout/1e6*15:.2f}")
    cross()
