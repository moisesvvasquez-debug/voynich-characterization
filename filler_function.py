# -*- coding: latin-1 -*-
# Idea del usuario: caracterizamos los rellenos pero no los AGREGAMOS.
#  A) quitar rellenos (prefijo/sufijo) -> nucleo; agrupar palabras que "valen igual".
#  B) ¿los rellenos tienen FUNCION? = ¿el prefijo se predice por seccion (MI vs nulo)
#     o es azar (puro relleno)?
import re, math, random
from collections import Counter, defaultdict
random.seed(7)

SEC={"H":"Herbal","A":"Astron","Z":"Zodiaco","B":"Biolog","C":"Cosmo","P":"Farma","S":"Estrellas","T":"Texto"}
PRE=["qok","qot","qo","cth","ckh","cph","cfh","ch","sh","ok","ot","yk","yt","yp","q","o","y","d","s"]
SUF=["aiin","aiir","ain","air","eedy","edy","eey","dy","ol","or","al","ar","am","an","in","ir","y","l","r","n"]
PRE.sort(key=len,reverse=True); SUF.sort(key=len,reverse=True)

def decomp(w):
    p=""; s=""
    for pr in PRE:
        if w.startswith(pr) and len(w)-len(pr)>=1: p=pr; break
    rest=w[len(p):]
    for sf in SUF:
        if rest.endswith(sf) and len(rest)-len(sf)>=1: s=sf; break
    core=rest[:len(rest)-len(s)] if s else rest
    return p,core,s

def load():
    toks=[]; cur=None
    for raw in open("voy_lsi.txt",encoding="latin-1"):
        m=re.search(r"\$I=([A-Z])",raw)
        if m: cur=m.group(1)
        mm=re.match(r"^<f[0-9]+[rv][0-9]?\.[0-9]+,[^;]*;H>\s+(.*)",raw)
        if not mm: continue
        body=mm.group(1).strip().rstrip("<->").strip()
        for w in re.split(r"[.,]",body):
            w=w.strip()
            if w and w.isascii() and w.isalpha(): toks.append((w.lower(),cur))
    return toks

toks=load()
words=[w for w,_ in toks]
print(f"tokens={len(words)}  types={len(set(words))}")

# ---------- A) clases de equivalencia por nucleo ----------
by_core=defaultdict(set); core_tokens=Counter()
for w in words:
    p,c,s=decomp(w)
    by_core[c].add(w); core_tokens[c]+=1
print(f"\nA) NUCLEOS: {len(by_core)} nucleos distintos generan {len(set(words))} palabras-tipo")
print("   nucleos mas 'productivos' (mas palabras-superficie distintas cuelgan de el):")
fam=sorted(by_core.items(), key=lambda kv:-len(kv[1]))[:8]
for c,forms in fam:
    ex=sorted(forms,key=len)[:6]
    print(f"   nucleo '{c or '(vacio)'}': {len(forms)} formas, {core_tokens[c]} tokens  ej: {', '.join(ex)}")

# ¿cuanto colapsa el vocabulario al quitar solo el prefijo?
strip_pre=Counter();
for w in words:
    p,c,s=decomp(w); strip_pre[c+s]+=1
print(f"\n   quitando SOLO prefijo: {len(set(words))} tipos -> {len(strip_pre)} (colapso {100*(1-len(strip_pre)/len(set(words))):.0f}%)")
# q como relleno: ¿qX tiene X atestiguado?
qw=[w for w in set(words) if w.startswith("q")]
has_base=sum(1 for w in qw if w[1:] in set(words))
print(f"   palabras con q- inicial: {len(qw)}; su version sin q tambien existe: {has_base} ({100*has_base/len(qw):.0f}%)")

# ---------- B) ¿el relleno (prefijo) tiene funcion? MI(prefijo;seccion) ----------
def mi(pairs):
    j=Counter(pairs); a=Counter(x for x,_ in pairs); b=Counter(y for _,y in pairs); N=len(pairs)
    return sum((n/N)*math.log2((n/N)/((a[x]/N)*(b[y]/N))) for (x,y),n in j.items())

pairs=[(decomp(w)[0] or "0", sec) for w,sec in toks if sec in SEC]
mi_ps=mi(pairs)
# nulo: barajar secciones
null=[]
secs=[y for _,y in pairs]
for _ in range(200):
    random.shuffle(secs)
    null.append(mi([(pairs[i][0],secs[i]) for i in range(len(pairs))]))
mnull=sum(null)/len(null); sd=(sum((x-mnull)**2 for x in null)/len(null))**.5
z=(mi_ps-mnull)/sd if sd else 0
print(f"\nB) MI(prefijo ; seccion) = {mi_ps:.4f} bits | nulo barajado {mnull:.4f}±{sd:.4f} | z={z:+.1f}")
print("   -> el prefijo/relleno " + ("SI carga funcion (depende de la seccion)" if z>3 else "NO depende de la seccion"))

# ¿que prefijo prefiere cada seccion? (funcion concreta del relleno)
print("\n   prefijo dominante por seccion (relleno = marcador de dominio):")
sec_pre=defaultdict(Counter)
for w,sec in toks:
    if sec in SEC: sec_pre[sec][decomp(w)[0] or "(none)"]+=1
for sec in ["H","B","S","P","Z","C","A"]:
    if sec in sec_pre and sum(sec_pre[sec].values())>200:
        top=sec_pre[sec].most_common(4)
        tot=sum(sec_pre[sec].values())
        print(f"   {SEC[sec]:<10}: "+", ".join(f"{p}={100*n/tot:.0f}%" for p,n in top))

# q-presence por seccion (¿el relleno q es azar o marca dominio?)
print("\n   tasa de q- inicial por seccion:")
for sec in ["H","B","S","P","Z","C"]:
    ws=[w for w,s in toks if s==sec]
    if len(ws)>200:
        print(f"   {SEC[sec]:<10}: {100*sum(1 for w in ws if w.startswith('q'))/len(ws):.0f}% de palabras")
