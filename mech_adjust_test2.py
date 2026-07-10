# -*- coding: utf-8 -*-
# TANDA 2: escalera de AJUSTES MECÁNICOS. ¿Qué combinación reproduce las 3 firmas juntas
# (entropía baja + templateado alto + enganche inter-palabra)? Todo mindless (sin sentido).
import re, math, random
from collections import Counter, defaultdict
random.seed(9)
PRE=['qok','qot','qo','cth','ckh','cph','cfh','ch','sh','ok','ot','yk','yt','yp','q','o','y','d','s']; PRE.sort(key=len,reverse=True)
SUF=['aiin','aiir','ain','air','eedy','edy','eey','dy','ol','or','al','ar','am','an','in','ir','y','l','r','n']; SUF.sort(key=len,reverse=True)
def dec(w):
    p=next((x for x in PRE if w.startswith(x) and len(w)-len(x)>=1),'')
    r=w[len(p):]; s=next((x for x in SUF if r.endswith(x) and len(r)-len(x)>=1),'')
    core=r[:len(r)-len(s)] if s else r
    return (p or '0'),(core or ''),(s or '0')
lines=[]; fol=[]
for raw in open('voy_lsi.txt',encoding='latin-1'):
    hm=re.match(r'^<(f[0-9]+[rv][0-9]?)\.',raw)
    m=re.match(r'^<f[0-9]+[rv][0-9]?\.[0-9]+,[^;]*;H>\s+(.*)',raw)
    if not m: continue
    ws=[t.strip().lower() for t in re.split(r'[.,]',m.group(1).strip()) if t.strip() and t.strip().isascii() and t.strip().isalpha()]
    if ws: lines.append([dec(w) for w in ws]); fol.append(hm.group(1) if hm else '?')
allw=[c for L in lines for c in L]
# distribuciones
Ppre=Counter(p for p,_,_ in allw); Pcore=Counter(c for _,c,_ in allw); Psuf=Counter(s for _,_,s in allw)
Ppre_ps=defaultdict(Counter); Psuf_p=defaultdict(Counter); Pcore_ps=defaultdict(Counter); Pcore_p=defaultdict(Counter)
for L in lines:
    for i,(p,c,s) in enumerate(L):
        Psuf_p[p][s]+=1; Pcore_ps[(p,s)][c]+=1; Pcore_p[p][c]+=1
        if i>0: Ppre_ps[L[i-1][2]][p]+=1
def draw(cnt):
    tot=sum(cnt.values()); r=random.random()*tot
    for k,n in cnt.items():
        r-=n
        if r<=0: return k
    return k
def dc(cond,key,*fbs):
    c=cond.get(key)
    if c: return draw(c)
    for fb in fbs:
        if isinstance(fb,dict):
            cc=fb.get(key)
            if cc: return draw(cc)
        else: return draw(fb)
    return draw(fbs[-1])
def build(p,c,s): return (p if p!='0' else '')+c+(s if s!='0' else '')
def gen(link=False, corecpl=False, sufcpl=False):
    out=[]
    for L in lines:
        ps='0'
        for _ in L:
            p = dc(Ppre_ps, ps, Ppre) if link else draw(Ppre)
            s = dc(Psuf_p, p, Psuf) if sufcpl else draw(Psuf)
            c = dc(Pcore_ps, (p,s), Pcore_p, Pcore) if corecpl else draw(Pcore)
            out.append((build(p,c,s),p,s)); ps=s
    return out
def h2(surf):
    st=" ".join(surf); bi=Counter(zip(st,st[1:])); uni=Counter(st); N=sum(bi.values())
    return -sum((n/N)*math.log2(n/uni[a]) for (a,b),n in bi.items())
def templ(surf,k=15):
    pr=Counter(w[:2] for w in surf if len(w)>=2); su=Counter(w[-2:] for w in surf if len(w)>=2)
    tp=set(x for x,_ in pr.most_common(k)); ts=set(x for x,_ in su.most_common(k))
    return 100*sum(1 for w in surf if len(w)>=2 and w[:2] in tp and w[-2:] in ts)/len(surf)
def milink(recs):
    pairs=[]; idx=0
    for L in lines:
        seg=recs[idx:idx+len(L)]; idx+=len(L)
        for i in range(len(seg)-1): pairs.append((seg[i][2], seg[i+1][1]))
    j=Counter(pairs); a=Counter(x for x,_ in pairs); b=Counter(y for _,y in pairs); N=len(pairs)
    return sum((n/N)*math.log2((n/N)/((a[x]/N)*(b[y]/N))) for (x,y),n in j.items())

V=[(build(*w),w[0],w[2]) for w in allw]
print(f"{'modelo':<40}{'h2':>7}{'templ%':>9}{'enganche':>11}")
print(f"{'VOYNICH real (objetivo)':<40}{h2([x[0] for x in V]):>7.2f}{templ([x[0] for x in V]):>9.1f}{milink(V):>11.4f}")
cfgs=[('M0 i.i.d. (sin ajuste)',dict()),
      ('M1 +enganche (pre|suf_prev)',dict(link=True)),
      ('M2 +núcleo acoplado',dict(link=True,corecpl=True)),
      ('M3 +sufijo|prefijo',dict(link=True,corecpl=True,sufcpl=True))]
for name,kw in cfgs:
    g=gen(**kw); print(f"{name:<40}{h2([x[0] for x in g]):>7.2f}{templ([x[0] for x in g]):>9.1f}{milink(g):>11.4f}")
print("\nobjetivo: h2≈2.12 · templ≈68.8 · enganche≈0.110")
print("KTD: si algún modelo mecánico alcanza LAS TRES => una máquina de engranajes sin sentido explica todo.")
print("     si queda una brecha => hay estructura que el ajuste mecánico no alcanza (finísima, dentro de palabra).")
