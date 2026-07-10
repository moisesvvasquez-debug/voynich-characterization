# -*- coding: utf-8 -*-
# TANDA 1: ¿un AJUSTE MECÁNICO en la máquina simulada reproduce el enganche inter-palabra?
# M0 = i.i.d. (sin ajuste)  ·  M1 = acoplamiento mecánico (prefijo_i+1 | sufijo_i, y suf|pre interno)
# Si M1 reproduce el enganche (0.11) + entropía + templateado => el enganche es MECÁNICO, no sentido.
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
# aprender de Voynich (por línea, para las transiciones)
lines=[]
for raw in open('voy_lsi.txt',encoding='latin-1'):
    m=re.match(r'^<f[0-9]+[rv][0-9]?\.[0-9]+,[^;]*;H>\s+(.*)',raw)
    if not m: continue
    ws=[t.strip().lower() for t in re.split(r'[.,]',m.group(1).strip()) if t.strip() and t.strip().isascii() and t.strip().isalpha()]
    if ws: lines.append([dec(w) for w in ws])
allw=[c for L in lines for c in L]
Ppre=Counter(p for p,_,_ in allw); Pcore=Counter(c for _,c,_ in allw); Psuf=Counter(s for _,_,s in allw)
Ppre_prevsuf=defaultdict(Counter); Psuf_pre=defaultdict(Counter)
for L in lines:
    for i,(p,c,s) in enumerate(L):
        Psuf_pre[p][s]+=1
        if i>0: Ppre_prevsuf[L[i-1][2]][p]+=1
def draw(counter):
    tot=sum(counter.values()); r=random.random()*tot
    for k,n in counter.items():
        r-=n
        if r<=0: return k
    return k
def draw_cond(cond, key, fallback):
    c=cond.get(key)
    return draw(c) if c else draw(fallback)
def build(word):
    p,c,s=word; return (p if p!='0' else '')+c+(s if s!='0' else '')
def gen(mode):
    out=[]  # (surface, pre, suf)
    for L in lines:
        prev_s='0'
        for _ in L:
            if mode=='M0':
                p=draw(Ppre); c=draw(Pcore); s=draw(Psuf)
            else: # M1 acoplamiento mecánico
                p=draw_cond(Ppre_prevsuf, prev_s, Ppre); c=draw(Pcore); s=draw_cond(Psuf_pre, p, Psuf)
            out.append((build((p,c,s)),p,s)); prev_s=s
    return out

def h2(surf):
    st=" ".join(surf); bi=Counter(zip(st,st[1:])); uni=Counter(st); N=sum(bi.values())
    return sum((n/N)*math.log2(n/uni[a]) for (a,b),n in bi.items())
def templ(surf,k=15):
    pre=Counter(w[:2] for w in surf if len(w)>=2); suf=Counter(w[-2:] for w in surf if len(w)>=2)
    tp=set(x for x,_ in pre.most_common(k)); ts=set(x for x,_ in suf.most_common(k))
    return 100*sum(1 for w in surf if len(w)>=2 and w[:2] in tp and w[-2:] in ts)/len(surf)
def mi_link(recs):  # MI(suf_i ; pre_i+1) usando los componentes conocidos, por línea
    pairs=[]; idx=0
    for L in lines:
        seg=recs[idx:idx+len(L)]; idx+=len(L)
        for i in range(len(seg)-1): pairs.append((seg[i][2], seg[i+1][1]))
    j=Counter(pairs); a=Counter(x for x,_ in pairs); b=Counter(y for _,y in pairs); N=len(pairs)
    return sum((n/N)*math.log2((n/N)/((a[x]/N)*(b[y]/N))) for (x,y),n in j.items())

Vsurf=[build(w) for w in allw]
Vrec=[(build(w),w[0],w[2]) for w in allw]
print(f"{'':<28}{'h2':>7}{'templ%':>9}{'MI enganche':>13}")
print(f"{'VOYNICH (real)':<28}{h2(Vsurf):>7.2f}{templ(Vsurf):>9.1f}{mi_link(Vrec):>13.4f}")
for mode,name in [('M0','Máquina i.i.d. (sin ajuste)'),('M1','Máquina con AJUSTE mecánico')]:
    g=gen(mode); print(f"{name:<28}{h2([x[0] for x in g]):>7.2f}{templ([x[0] for x in g]):>9.1f}{mi_link(g):>13.4f}")
print("\nKTD: si M1 ≈ Voynich en las 3 (incluido el enganche ~0.11) => un ajuste MECÁNICO reproduce todo;")
print("     el enganche NO es evidencia de sentido, sino una máquina de engranaje acoplado.")
