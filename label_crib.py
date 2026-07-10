#!/usr/bin/env python3
"""
PASO 2-3 del test de ETIQUETAS: el crib con referente TIGHT.
Cada etiqueta apunta a UN objeto dibujado (parte de planta en la farmacéutica).
Pregunta: ¿el ajuste del dial de una etiqueta (prefijo/sufijo/núcleo) predice el
TIPO de parte que rotula, por encima del azar y fuera de muestra?

Flujo:
  1) lee labels.json (etiquetas por folio en orden de lectura, del paso 1).
  2) VISIÓN (Claude): por cada folio-objetivo, lista los objetos rotulados EN ORDEN DE LECTURA
     -> [{part_type,color,shape}]. Se guarda label_objects.json.
  3) EMPAREJA etiqueta[i] <-> objeto[i] por índice, con COMPUERTA de conteo
     (si #objetos != #etiquetas del folio -> se marca desalineado y se excluye del test estricto).
  4) CRUCE: para prefijo y sufijo, ¿las etiquetas con el mismo afijo caen sobre el mismo
     part_type por encima de un nulo por permutación? + versión OUT-OF-SAMPLE (split folios).

Uso:  python3 label_crib.py --folios f99r,f100r,f101r,f102r,f88r,f89r --model claude-sonnet-5
      python3 label_crib.py --cross-only     (re-cruza sin re-anotar)
Key en ~/voynich-poc/.anthropic_key (igual que vision_pipeline_claude.py).
"""
import os, re, json, base64, argparse, collections, math, random, subprocess, urllib.request, pathlib
random.seed(0)
HERE=os.path.dirname(os.path.abspath(__file__))
OBJ=os.path.join(HERE,"label_objects.json")
API="https://api.anthropic.com/v1/messages"

def api_key():
    f=pathlib.Path(HERE)/".anthropic_key"
    if f.exists(): return f.read_text().strip()
    k=os.environ.get("ANTHROPIC_API_KEY")
    if k: return k.strip()
    raise SystemExit("Falta la key en ~/voynich-poc/.anthropic_key")

# folio -> scan. La fórmula n=2·folio-1 SOLO vale en el herbario (hojas simples);
# tras los foldouts el numerado de archive.org se corre. Override verificado por número de esquina:
SCAN_OVERRIDE={"f99r":175,"f99v":176,"f100r":177,"f100v":178,"f101r":179,"f101v":180,"f102r":181,"f102v":182}
def folio_to_scan(fol):
    if fol in SCAN_OVERRIDE: return SCAN_OVERRIDE[fol]
    m=re.match(r"f(\d+)([rv])",fol); num=int(m.group(1)); side=m.group(2)
    return num*2-1 if side=="r" else num*2

def get_scan(fol):
    n=folio_to_scan(fol)
    p=os.path.join(HERE,"scans",f"{n:03d}.jpg")
    if os.path.exists(p) and os.path.getsize(p)>0: return p
    tmp=f"/tmp/lbl_{n}.jpg"
    urllib.request.urlretrieve(f"https://archive.org/download/voynich/{n:03d}.jpg",tmp)
    subprocess.run(["sips","-Z","2000",tmp,"--out",p],capture_output=True)
    try: os.remove(tmp)
    except OSError: pass
    return p

PROMPT=(
"This is a PHARMACEUTICAL page of the Voynich manuscript: detached, individually-drawn plant PARTS "
"(roots, leaves, flowers, seed-pods), several of them sitting in decorated apothecary jars, and each drawn "
"object has a short handwritten LABEL next to it. IGNORE the script (you cannot read it). "
"List the LABELLED drawn objects in READING ORDER — top block first, then within each row left-to-right, "
"exactly as a scribe's labels would run. One entry per labelled object. Return ONLY strict JSON:\n"
'{"n_labeled_objects": <int>, "objects":[\n'
'  {"part":"root|leaf|flower|seedpod|stem|whole_plant|jar_only|other",'
'   "in_jar":true|false,'
'   "color":"green|brown|red|blue|yellow|white|mixed|other",'
'   "shape":"<one short phrase>"}\n'
']}'
)

def annotate(model,key,img):
    b64=base64.b64encode(open(img,"rb").read()).decode()
    body=json.dumps({"model":model,"max_tokens":3000,"messages":[{"role":"user","content":[
        {"type":"image","source":{"type":"base64","media_type":"image/jpeg","data":b64}},
        {"type":"text","text":PROMPT}]}]}).encode()
    req=urllib.request.Request(API,data=body,headers={
        "x-api-key":key,"anthropic-version":"2023-06-01","content-type":"application/json"})
    with urllib.request.urlopen(req,timeout=180) as r: out=json.load(r)
    txt="".join(b.get("text","") for b in out.get("content",[]) if b.get("type")=="text")
    m=re.search(r"\{.*\}",txt,re.S)
    rec=json.loads(m.group(0)) if m else {"objects":[],"raw":txt[:200]}
    rec["_in"]=out.get("usage",{}).get("input_tokens"); rec["_out"]=out.get("usage",{}).get("output_tokens")
    return rec

# ---------------- CRUCE ----------------
def cross():
    labels=json.load(open(os.path.join(HERE,"labels.json")))
    objs=json.load(open(OBJ)) if os.path.exists(OBJ) else {}
    aligned=[]   # (folio, {pre,core,suf}, part) para etiquetas emparejadas
    report=[]
    for fol,objrec in objs.items():
        L=labels.get(fol,[]); O=objrec.get("objects",[])
        # compuerta flexible: |ΔN|<=2 y empatar los primeros min(n) por índice de lectura
        ok = (len(L)>0 and len(O)>0 and abs(len(L)-len(O))<=2)
        report.append((fol,len(L),len(O),"empareja(±2)" if ok else "DESCARTADO"))
        if not ok: continue
        for i in range(min(len(L),len(O))):
            d=L[i]["dec"]
            if d: aligned.append((fol,tuple(d),O[i].get("part")))
    print("=== EMPAREJAMIENTO (compuerta de conteo etiqueta vs objeto) ===")
    for fol,nl,no,st in report: print(f"  {fol:7} etiquetas={nl:3} objetos={no:3}  -> {st}")
    print(f"\netiquetas emparejadas y descompuestas: {len(aligned)}")
    if len(aligned)<20:
        print("MUESTRA INSUFICIENTE para el test estricto (se necesita más folios alineados)."); return

    parts=[a[2] for a in aligned]
    base=collections.Counter(parts); B=sum(base.values())
    print("baseline part_type:", {k:f'{100*v/B:.0f}%' for k,v in base.most_common()})

    def strength(rows,comp):  # comp: 0=pre,2=suf
        # nº de afijos cuyas etiquetas se concentran en un part_type con lift>=1.6, frac>=0.6, n>=4
        byaff=collections.defaultdict(list)
        for fol,d,part in rows:
            if part: byaff[d[comp]].append(part)
        s=0
        for aff,ps in byaff.items():
            if len(ps)<4: continue
            c=collections.Counter(ps); top,n=c.most_common(1)[0]; frac=n/len(ps)
            lift=frac/(base.get(top,0)/B) if base.get(top,0) else 0
            if frac>=0.6 and lift>=1.6: s+=1
        return s

    for comp,name in [(0,"PREFIJO"),(2,"SUFIJO")]:
        real=strength(aligned,comp)
        nulls=[]
        ps=[a[2] for a in aligned]
        for _ in range(1000):
            sh=ps[:]; random.shuffle(sh)
            rows=[(aligned[i][0],aligned[i][1],sh[i]) for i in range(len(aligned))]
            nulls.append(strength(rows,comp))
        mx=max(nulls); mean=sum(nulls)/len(nulls)
        print(f"\n[{name}] señales fuertes REAL={real}  nulo barajado media={mean:.1f} max={mx}")
        print("  VEREDICTO:", "POSIBLE CRIB (real>nulo)" if real>mx else "NULO (real<=nulo) = sin código en etiquetas")

    # OUT-OF-SAMPLE: aprender mapping afijo->part en la mitad de folios, testear en la otra
    fols=sorted(set(a[0] for a in aligned)); random.shuffle(fols)
    half=set(fols[:len(fols)//2])
    for comp,name in [(0,"PREFIJO"),(2,"SUFIJO")]:
        train=collections.defaultdict(collections.Counter)
        for fol,d,part in aligned:
            if fol in half and part: train[d[comp]][part]+=1
        pred=lambda aff: train[aff].most_common(1)[0][0] if train.get(aff) else None
        hit=tot=0
        for fol,d,part in aligned:
            if fol not in half and part:
                p=pred(d[comp])
                if p is not None: tot+=1; hit+= (p==part)
        acc=hit/tot if tot else 0
        naive=base.most_common(1)[0][1]/B
        print(f"[{name} OUT-OF-SAMPLE] acc={acc:.2f} (n={tot})  vs naive(mayoría)={naive:.2f}  -> "
              + ("SUPERA naive" if acc>naive+0.05 else "no supera naive"))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--folios",default="")
    ap.add_argument("--model",default="claude-sonnet-5")
    ap.add_argument("--cross-only",action="store_true")
    a=ap.parse_args()
    if a.cross_only: cross(); raise SystemExit
    labels=json.load(open(os.path.join(HERE,"labels.json")))
    fols=[f.strip() for f in a.folios.split(",") if f.strip()] or \
         sorted(labels, key=lambda f:-len(labels[f]))[:8]  # los 8 más ricos por defecto
    key=api_key(); out=json.load(open(OBJ)) if os.path.exists(OBJ) else {}
    tin=tout=0
    for fol in fols:
        if fol in out: print(f"{fol}: ya anotado, salto"); continue
        try:
            r=annotate(a.model,key,get_scan(fol))
            out[fol]=r; tin+=r.get("_in") or 0; tout+=r.get("_out") or 0
            n=r.get("n_labeled_objects","?"); nl=len(labels.get(fol,[]))
            print(f"{fol}: visión ve {n} objetos rotulados | transliteración tiene {nl} etiquetas "
                  + ("(alinea)" if n==nl else "(NO alinea)"))
            json.dump(out,open(OBJ,"w"))
        except Exception as e:
            print(f"{fol}: ERROR {e}")
    print(f"\ntokens in={tin:,} out={tout:,}  costo aprox Sonnet ${tin/1e6*3+tout/1e6*15:.2f}")
    cross()
