# -*- coding: latin-1 -*-
# Hipotesis usuario: uno de los slots = CALIFICACION cualitativa (pos/neutro/neg y variaciones).
# Un "grado" debe ser: (a) POCOS valores, (b) TRANSVERSAL a dominios (aplica a todo),
# (c) se pega LIBRE a cualquier item (bajo acoplamiento con el nucleo).
import re, math
from collections import Counter, defaultdict

SEC={"H","A","Z","B","C","P","S"}
PRE=["qok","qot","qo","cth","ckh","cph","cfh","ch","sh","ok","ot","yk","yt","yp","q","o","y","d","s"]
SUF=["aiin","aiir","ain","air","eedy","edy","eey","dy","ol","or","al","ar","am","an","in","ir","y","l","r","n"]
PRE.sort(key=len,reverse=True); SUF.sort(key=len,reverse=True)
def dec(w):
    p=next((x for x in PRE if w.startswith(x) and len(w)-len(x)>=1),"")
    rest=w[len(p):]
    s=next((x for x in SUF if rest.endswith(x) and len(rest)-len(x)>=1),"")
    core=rest[:len(rest)-len(s)] if s else rest
    return p or "0", core or "0", s or "0"

toks=[]; cur=None
for raw in open("voy_lsi.txt",encoding="latin-1"):
    m=re.search(r"\$I=([A-Z])",raw)
    if m: cur=m.group(1)
    mm=re.match(r"^<f[0-9]+[rv][0-9]?\.[0-9]+,[^;]*;H>\s+(.*)",raw)
    if not mm: continue
    for w in re.split(r"[.,]",mm.group(1).strip().rstrip("<->").strip()):
        w=w.strip()
        if w and w.isascii() and w.isalpha() and cur in SEC: toks.append((w.lower(),cur))

P=[dec(w)[0] for w,_ in toks]; C=[dec(w)[1] for w,_ in toks]; S=[dec(w)[2] for w,_ in toks]
sec=[s for _,s in toks]; N=len(toks)

def H(xs):
    c=Counter(xs); return -sum((n/len(xs))*math.log2(n/len(xs)) for n in c.values())
def MI(xs,ys):
    j=Counter(zip(xs,ys)); a=Counter(xs); b=Counter(ys); n=len(xs)
    return sum((v/n)*math.log2((v/n)/((a[x]/n)*(b[y]/n))) for (x,y),v in j.items())

print(f"tokens={N}\n")
print(f"{'slot':<8}{'#valores':>9}{'#eff(2^H)':>11}{'U(sec|slot)':>13}{'U(slot|core)':>14}")
for lab,X in [("prefijo",P),("nucleo",C),("sufijo",S)]:
    nv=len(set(X)); eff=2**H(X)
    u_sec = MI(X,sec)/H(sec)              # cuanto del dominio explica el slot (0=general)
    u_core= MI(X,C)/H(X) if lab!="nucleo" else 0.0   # acoplamiento con el item (0=libre)
    print(f"{lab:<8}{nv:>9}{eff:>11.1f}{u_sec:>13.3f}{u_core:>14.3f}")
print("\n  grado ideal = #eff CHICO + U(sec|slot) BAJO(transversal) + U(slot|core) BAJO(libre)")

# ¿el sufijo se pega libre a cualquier item? tasa: de los cores frecuentes, cuantos sufijos distintos toman
core_suf=defaultdict(set)
for c,s in zip(C,S): core_suf[c].add(s)
cn=Counter(C); freq=[c for c in cn if cn[c]>=30]
avg_suf=sum(len(core_suf[c]) for c in freq)/len(freq)
print(f"\n  cores frecuentes (n>=30): {len(freq)}; sufijos distintos por core (media): {avg_suf:.1f} de {len(set(S))}")
print("  -> si un core toma MUCHOS sufijos, el sufijo NO es lexico -> compatible con grado libre")

# ¿los sufijos ordenan en 1D? (grado = escala ordinal). PCA casero sobre sufijo x seccion.
sufs=[s for s,_ in Counter(S).most_common(8)]
rows=[]
for s in sufs:
    d=Counter(sc for ss,sc in zip(S,sec) if ss==s); tot=sum(d.values())
    rows.append([d.get(k,0)/tot for k in sorted(SEC)])
# centrar
import math as _m
means=[sum(r[j] for r in rows)/len(rows) for j in range(len(rows[0]))]
Xc=[[r[j]-means[j] for j in range(len(r))] for r in rows]
# covarianza y potencia para PC1 (power iteration)
def matvec(M,v): return [sum(M[i][j]*v[j] for j in range(len(v))) for i in range(len(M))]
# cov = Xc^T Xc
cols=len(Xc[0]); cov=[[sum(Xc[k][i]*Xc[k][j] for k in range(len(Xc))) for j in range(cols)] for i in range(cols)]
v=[1.0]*cols
for _ in range(200):
    v=matvec(cov,v); nrm=_m.sqrt(sum(x*x for x in v)) or 1; v=[x/nrm for x in v]
lam1=sum(v[i]*sum(cov[i][j]*v[j] for j in range(cols)) for i in range(cols))
tot=sum(cov[i][i] for i in range(cols))
print(f"\n  ordinalidad sufijos: varianza en PC1 = {100*lam1/tot:.0f}% (alto=escala 1D/ordinal; bajo=categorias nominales)")
