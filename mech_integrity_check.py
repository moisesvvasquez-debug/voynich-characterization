# -*- coding: utf-8 -*-
# PRUEBA DE INTEGRIDAD del modelo mecánico M3 (antes de meterlo al paper):
#  (1) FUERA DE MUESTRA: ajustar en la mitad de folios, evaluar en la otra mitad (nunca vista).
#  (2) NOVEDAD: ¿genera palabras NUEVAS (generaliza) o solo copia el texto (memoriza)?
import re, math, random
from collections import Counter, defaultdict
random.seed(11)
PRE=['qok','qot','qo','cth','ckh','cph','cfh','ch','sh','ok','ot','yk','yt','yp','q','o','y','d','s']; PRE.sort(key=len,reverse=True)
SUF=['aiin','aiir','ain','air','eedy','edy','eey','dy','ol','or','al','ar','am','an','in','ir','y','l','r','n']; SUF.sort(key=len,reverse=True)
def dec(w):
    p=next((x for x in PRE if w.startswith(x) and len(w)-len(x)>=1),'')
    r=w[len(p):]; s=next((x for x in SUF if r.endswith(x) and len(r)-len(x)>=1),'')
    core=r[:len(r)-len(s)] if s else r
    return (p or '0'),(core or ''),(s or '0')
lines=[]; fols=[]
for raw in open('voy_lsi.txt',encoding='latin-1'):
    hm=re.match(r'^<(f[0-9]+[rv][0-9]?)\.',raw)
    m=re.match(r'^<f[0-9]+[rv][0-9]?\.[0-9]+,[^;]*;H>\s+(.*)',raw)
    if not m: continue
    ws=[t.strip().lower() for t in re.split(r'[.,]',m.group(1).strip()) if t.strip() and t.strip().isascii() and t.strip().isalpha()]
    if ws: lines.append([dec(w) for w in ws]); fols.append(hm.group(1) if hm else '?')
# split por folio (par/impar en orden de aparición) => train / test disjuntos
uniq=[]; seen=set()
for f in fols:
    if f not in seen: seen.add(f); uniq.append(f)
trainf=set(uniq[::2]);
TR=[L for L,f in zip(lines,fols) if f in trainf]
TE=[L for L,f in zip(lines,fols) if f not in trainf]
def fit(LS):
    d={'pre':Counter(),'core':Counter(),'suf':Counter(),'pps':defaultdict(Counter),'sp':defaultdict(Counter),'cps':defaultdict(Counter),'cp':defaultdict(Counter)}
    for L in LS:
        for i,(p,c,s) in enumerate(L):
            d['pre'][p]+=1; d['core'][c]+=1; d['suf'][s]+=1
            d['sp'][p][s]+=1; d['cps'][(p,s)][c]+=1; d['cp'][p][c]+=1
            if i>0: d['pps'][L[i-1][2]][p]+=1
    return d
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
def gen(d, structure):  # M3 completo, con la estructura de líneas de 'structure'
    out=[]
    for L in structure:
        ps='0'
        for _ in L:
            p=dc(d['pps'],ps,d['pre']); s=dc(d['sp'],p,d['suf']); c=dc(d['cps'],(p,s),d['cp'],d['core'])
            out.append((build(p,c,s),p,s)); ps=s
    return out
def h2(surf):
    st=" ".join(surf); bi=Counter(zip(st,st[1:])); uni=Counter(st); N=sum(bi.values())
    return -sum((n/N)*math.log2(n/uni[a]) for (a,b),n in bi.items())
def templ(surf,k=15):
    pr=Counter(w[:2] for w in surf if len(w)>=2); su=Counter(w[-2:] for w in surf if len(w)>=2)
    tp=set(x for x,_ in pr.most_common(k)); ts=set(x for x,_ in su.most_common(k))
    return 100*sum(1 for w in surf if len(w)>=2 and w[:2] in tp and w[-2:] in ts)/len(surf)
def milink(recs,structure):
    pairs=[]; idx=0
    for L in structure:
        seg=recs[idx:idx+len(L)]; idx+=len(L)
        for i in range(len(seg)-1): pairs.append((seg[i][2], seg[i+1][1]))
    j=Counter(pairs); a=Counter(x for x,_ in pairs); b=Counter(y for _,y in pairs); N=len(pairs)
    return sum((n/N)*math.log2((n/N)/((a[x]/N)*(b[y]/N))) for (x,y),n in j.items())
def stats(recs,structure):
    surf=[r[0] for r in recs]; return h2(surf),templ(surf),milink(recs,structure)

dtrain=fit(TR)
# objetivo = TEST real (mitad nunca vista)
TErec=[(build(*w),w[0],w[2]) for L in TE for w in L]
th,tt,tl=stats(TErec,TE)
# modelo ajustado en TRAIN, generando la estructura del TEST
G=gen(dtrain,TE)
gh,gt,gl=stats(G,TE)
print("(1) FUERA DE MUESTRA  — ajustado en mitad TRAIN, evaluado en estructura del TEST (nunca visto)")
print(f"{'':<22}{'h2':>7}{'templ%':>9}{'enganche':>11}")
print(f"{'TEST real (objetivo)':<22}{th:>7.2f}{tt:>9.1f}{tl:>11.4f}")
print(f"{'M3 (out-of-sample)':<22}{gh:>7.2f}{gt:>9.1f}{gl:>11.4f}")
# novedad: tipos generados que NO están en el vocabulario de TRAIN
trainvocab=set(build(*w) for L in TR for w in L)
gtypes=set(r[0] for r in G)
novel=sum(1 for t in gtypes if t not in trainvocab)
# ¿qué fracción del vocab REAL del test es nuevo respecto a train? (piso de comparación)
tetypes=set(r[0] for r in TErec); tenovel=sum(1 for t in tetypes if t not in trainvocab)
print("\n(2) NOVEDAD  — ¿genera palabras nuevas o copia?")
print(f"  tipos generados: {len(gtypes)} · nuevos (no en TRAIN): {novel} ({100*novel/len(gtypes):.0f}%)")
print(f"  referencia: del vocab REAL del TEST, {tenovel}/{len(tetypes)} ({100*tenovel/len(tetypes):.0f}%) tampoco está en TRAIN")
print("\nLECTURA: si M3 out-of-sample ≈ TEST real en las 3, y genera % alto de palabras nuevas,")
print("         => el modelo mecánico GENERALIZA (no memoriza) y explica el texto de verdad.")
