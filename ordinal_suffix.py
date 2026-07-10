# -*- coding: latin-1 -*-
# ¿El eje ordinal (1D) de los sufijos se comporta como una escala NUMERICA/grado?
# Firma de un grado: al ordenar por el eje 1D, la FRECUENCIA baja monotona
# (grados bajos comunes, grados altos raros) y/o la LONGITUD sube (mas marcas = mas grado).
import re, math
from collections import Counter
SEC=sorted({"H","A","Z","B","C","P","S"})
SUF=["aiin","aiir","ain","air","eedy","edy","eey","dy","ol","or","al","ar","am","an","in","ir","y","l","r","n"]
SUF.sort(key=len,reverse=True)
PRE=["qok","qot","qo","cth","ckh","cph","cfh","ch","sh","ok","ot","yk","yt","yp","q","o","y","d","s"]
PRE.sort(key=len,reverse=True)
def suf_of(w):
    p=next((x for x in PRE if w.startswith(x) and len(w)-len(x)>=1),"")
    rest=w[len(p):]
    return next((x for x in SUF if rest.endswith(x) and len(rest)-len(x)>=1),"0")
toks=[]; cur=None
for raw in open("voy_lsi.txt",encoding="latin-1"):
    m=re.search(r"\$I=([A-Z])",raw)
    if m: cur=m.group(1)
    mm=re.match(r"^<f[0-9]+[rv][0-9]?\.[0-9]+,[^;]*;H>\s+(.*)",raw)
    if not mm: continue
    for w in re.split(r"[.,]",mm.group(1).strip().rstrip("<->").strip()):
        w=w.strip()
        if w and w.isascii() and w.isalpha() and cur in SEC: toks.append((w.lower(),cur))
S=[suf_of(w) for w,_ in toks]; sec=[s for _,s in toks]
top=[s for s,_ in Counter(S).most_common(8)]
# matriz sufijo x seccion (proporciones), centrar, PC1 direction, proyectar
rows={s:[0]*len(SEC) for s in top}
cnt=Counter(zip(S,sec))
for i,k in enumerate(SEC):
    for s in top: rows[s][i]=cnt.get((s,k),0)
for s in top:
    t=sum(rows[s]) or 1; rows[s]=[x/t for x in rows[s]]
means=[sum(rows[s][j] for s in top)/len(top) for j in range(len(SEC))]
Xc={s:[rows[s][j]-means[j] for j in range(len(SEC))] for s in top}
cov=[[sum(Xc[s][i]*Xc[s][j] for s in top) for j in range(len(SEC))] for i in range(len(SEC))]
v=[1.0]*len(SEC)
for _ in range(300):
    v=[sum(cov[i][j]*v[j] for j in range(len(SEC))) for i in range(len(SEC))]
    n=math.sqrt(sum(x*x for x in v)) or 1; v=[x/n for x in v]
coord={s:sum(Xc[s][j]*v[j] for j in range(len(SEC))) for s in top}
freq={s:S.count(s) for s in top}
order=sorted(top,key=lambda s:coord[s])
print("sufijos ordenados por el eje 1D (PC1):")
print(f"  {'suf':<6}{'coord':>8}{'freq':>8}{'|suf|':>7}")
for s in order:
    print(f"  {s:<6}{coord[s]:>8.3f}{freq[s]:>8}{len(s):>7}")
# ¿monotonia? correlacion de rango coord vs freq y vs longitud
def spear(xs,ys):
    rx={v:i for i,v in enumerate(sorted(xs))}; ry={v:i for i,v in enumerate(sorted(ys))}
    a=[rx[x] for x in xs]; b=[ry[y] for y in ys]; n=len(xs)
    ma=sum(a)/n; mb=sum(b)/n
    num=sum((a[i]-ma)*(b[i]-mb) for i in range(n))
    den=math.sqrt(sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b)) or 1
    return num/den
cs=[coord[s] for s in order]; fs=[freq[s] for s in order]; ls=[len(s) for s in order]
print(f"\n  corr(eje1D , frecuencia) = {spear(cs,fs):+.2f}")
print(f"  corr(eje1D , longitud)   = {spear(cs,ls):+.2f}")
print("  (monotonia fuerte = el eje se comporta como escala graduada/numerica)")
