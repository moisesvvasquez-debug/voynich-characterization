#!/usr/bin/env python3
"""
DERIVA (rotor) en TEXTO y en IMAGEN, sobre el mismo eje (posicion en el manuscrito).
1) control temporal: la deriva de sufijo, ¿es monotona (rotor que avanza) y especifica del
   sufijo (no del prefijo)? -> similitud por BIN de distancia + permutacion.
2) MISMO test en IMAGEN: ¿la morfologia de planta (annotations_claude) deriva con la posicion?
3) cruce honesto: ¿la similitud de imagen predice la de sufijo MAS ALLA de la distancia compartida?
   (correlacion parcial controlando distancia; ambas cosas derivan con la posicion -> confundido).
Salida: consola + drift_data.json para el grafico.
"""
import re, json, math, collections, random
random.seed(0)
HERE="."; PATH="voy_lsi.txt"

def folio_pos(fol):
    m=re.match(r"f(\d+)([rv])(\d*)",fol)
    if not m: return None
    num=int(m.group(1)); side=0 if m.group(2)=="r" else 1
    return num*2+side  # orden canonico del manuscrito

# ---------- TEXTO ----------
sec={}; words=collections.defaultdict(list)
for raw in open(PATH,encoding="latin-1"):
    h=re.match(r"^<(f[0-9]+[rv][0-9]?)>\s*<!\s*\$I=([A-Z])",raw)
    if h: sec[h.group(1)]=h.group(2); continue
    m=re.match(r"^<(f[0-9]+[rv][0-9]?)\.[0-9]+,[^;]*;H>\s+(.*)",raw)
    if not m: continue
    fol,body=m.groups()
    for tok in re.split(r"[.,]",body.strip()):
        tok=re.sub(r"[!%?*\-<>@=\s]","",tok)
        if tok and len(tok)>=2: words[fol].append(tok)
HERB=[f for f in words if sec.get(f)=="H" and len(words[f])>=25 and folio_pos(f)]

def aff_profile(fol,which):
    c=collections.Counter()
    for w in words[fol]: c[w[:2] if which=="pre" else w[-2:]]+=1
    return c

# ---------- IMAGEN ----------
FEATS=["root_form","root_color","stem_count","leaf_form","leaf_arrangement",
       "leaf_color","flower","flower_form","fruit","habit"]
img={}   # folio -> vector one-hot (dict)
for line in open("annotations_claude.jsonl"):
    try: d=json.loads(line)
    except Exception: continue
    fol=d.get("det_folio")
    if not fol or not folio_pos(fol): continue
    v={}
    for f in FEATS:
        val=d.get(f)
        if val not in (None,"none","na"): v[f+"="+str(val)]=1.0
    if v: img[fol]=v
IMG=list(img.keys())

def cosine(a,b):
    ks=set(a)|set(b); dot=sum(a.get(k,0)*b.get(k,0) for k in ks)
    na=math.sqrt(sum(x*x for x in a.values())); nb=math.sqrt(sum(x*x for x in b.values()))
    return dot/(na*nb) if na and nb else 0.0

def pearson(xs,ys):
    n=len(xs); mx=sum(xs)/n; my=sum(ys)/n
    cov=sum((xs[i]-mx)*(ys[i]-my) for i in range(n))
    sx=math.sqrt(sum((x-mx)**2 for x in xs)); sy=math.sqrt(sum((y-my)**2 for y in ys))
    return cov/(sx*sy) if sx and sy else 0.0

def pairs(folios,proffn):
    P={f:proffn(f) for f in folios}; pos={f:folio_pos(f) for f in folios}
    D=[]; S=[]
    fl=list(folios)
    for i in range(len(fl)):
        for j in range(i+1,len(fl)):
            D.append(abs(pos[fl[i]]-pos[fl[j]])); S.append(cosine(P[fl[i]],P[fl[j]]))
    return D,S

def analyze(name,folios,proffn,nbins=8):
    D,S=pairs(folios,proffn)
    r=pearson(D,S)
    # permutacion: barajar asignacion perfil<->folio (rompe relacion pos-perfil)
    nulls=[]
    fl=list(folios); prof={f:proffn(f) for f in fl}; pos={f:folio_pos(f) for f in fl}
    for _ in range(500):
        sh=fl[:]; random.shuffle(sh)
        mp={fl[k]:prof[sh[k]] for k in range(len(fl))}
        d=[];s=[]
        for i in range(len(fl)):
            for j in range(i+1,len(fl)):
                d.append(abs(pos[fl[i]]-pos[fl[j]])); s.append(cosine(mp[fl[i]],mp[fl[j]]))
        nulls.append(pearson(d,s))
    mean=sum(nulls)/len(nulls); sd=math.sqrt(sum((x-mean)**2 for x in nulls)/len(nulls))
    z=(r-mean)/sd if sd else 0; p=sum(1 for x in nulls if x<=r)/len(nulls)
    # binned decay (monotonia = rotor)
    mx=max(D); edges=[mx*(b+1)/nbins for b in range(nbins)]
    binned=[]
    for b in range(nbins):
        lo=0 if b==0 else edges[b-1]; hi=edges[b]
        vals=[S[k] for k in range(len(D)) if lo<D[k]<=hi] if b>0 else [S[k] for k in range(len(D)) if D[k]<=hi]
        binned.append({"d":round((lo+hi)/2,1),"sim":round(sum(vals)/len(vals),4) if vals else None,"n":len(vals)})
    print(f"[{name}] n_folios={len(folios)}  corr(sim,dist)={r:+.3f}  nulo {mean:+.3f}±{sd:.3f}  z={z:+.2f}  p={p:.3f}  "
          + ("DERIVA" if (p<0.05 and r<0) else "sin deriva"))
    return {"name":name,"r":round(r,4),"z":round(z,2),"p":round(p,4),"binned":binned,"n":len(folios)}

print("=== DERIVA POR CANAL (mismo eje = posicion en el manuscrito) ===")
res_pre=analyze("texto: PREFIJO",HERB,lambda f:aff_profile(f,"pre"))
res_suf=analyze("texto: SUFIJO",HERB,lambda f:aff_profile(f,"suf"))
res_img=analyze("imagen: MORFOLOGIA",IMG,lambda f:img[f])

# ---------- cruce honesto: imagen vs sufijo, controlando distancia ----------
common=[f for f in IMG if f in words and sec.get(f)=="H" and len(words[f])>=25]
print(f"\n=== CRUCE texto-sufijo <-> imagen (folios en ambos: {len(common)}) ===")
sp={f:aff_profile(f,"suf") for f in common}; ip={f:img[f] for f in common}; pos={f:folio_pos(f) for f in common}
D=[];Ssuf=[];Simg=[]
for i in range(len(common)):
    for j in range(i+1,len(common)):
        a,b=common[i],common[j]
        D.append(abs(pos[a]-pos[b])); Ssuf.append(cosine(sp[a],sp[b])); Simg.append(cosine(ip[a],ip[b]))
r_raw=pearson(Simg,Ssuf)
# parcial controlando distancia: residuos de cada uno vs D
def residuals(y,x):
    b=pearson(x,y)*(math.sqrt(sum((v-sum(y)/len(y))**2 for v in y))/math.sqrt(sum((v-sum(x)/len(x))**2 for v in x)))
    my=sum(y)/len(y); mx=sum(x)/len(x); a=my-b*mx
    return [y[k]-(a+b*x[k]) for k in range(len(y))]
r_par=pearson(residuals(Simg,D),residuals(Ssuf,D))
# permutacion del cruce parcial
nl=[]
idx=list(range(len(common)))
for _ in range(500):
    sh=common[:]; random.shuffle(sh)
    ip2={common[k]:img[sh[k]] for k in range(len(common))}
    si=[]
    for i in range(len(common)):
        for j in range(i+1,len(common)):
            si.append(cosine(ip2[common[i]],ip2[common[j]]))
    nl.append(pearson(residuals(si,D),residuals(Ssuf,D)))
mean=sum(nl)/len(nl); sd=math.sqrt(sum((x-mean)**2 for x in nl)/len(nl)); zc=(r_par-mean)/sd if sd else 0
pc=sum(1 for x in nl if x>=r_par)/len(nl)
print(f"corr(sim_imagen, sim_sufijo) bruta = {r_raw:+.3f}")
print(f"PARCIAL (controlando distancia)      = {r_par:+.3f}  nulo {mean:+.3f}±{sd:.3f}  z={zc:+.2f}  p={pc:.3f}")
print("=> "+("acoplamiento imagen<->sufijo MAS ALLA de la posicion" if pc<0.05 and r_par>0
      else "sin acoplamiento extra: ambos solo siguen la posicion (confundido esperado)"))

json.dump({"channels":[res_pre,res_suf,res_img],
           "cross":{"raw":round(r_raw,4),"partial":round(r_par,4),"z":round(zc,2),"p":round(pc,4),"n":len(common)}},
          open("drift_data.json","w"),indent=1)
print("\n-> drift_data.json escrito")
