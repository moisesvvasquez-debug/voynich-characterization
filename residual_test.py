# -*- coding: utf-8 -*-
# KTD #3: ¿las palabras NO-CONFORMES (que rompen la gramática de ranuras) son el CONTENIDO?
# Test: ¿cargan más señal de sección (especificidad KL) que las conformes? + dónde viven.
import re, math
from collections import Counter, defaultdict

SEC={"H","A","Z","B","C","P","S"}
PRE=["qok","qot","qo","cth","ckh","cph","cfh","ch","sh","ok","ot","yk","yt","yp","q","o","y","d","s"]; PRE.sort(key=len,reverse=True)
SUF=["aiin","aiir","ain","air","eedy","edy","eey","dy","ol","or","al","ar","am","an","in","ir","y","l","r","n"]; SUF.sort(key=len,reverse=True)
def dec(w):
    p=next((x for x in PRE if w.startswith(x) and len(w)-len(x)>=1),"")
    rest=w[len(p):]
    s=next((x for x in SUF if rest.endswith(x) and len(rest)-len(x)>=1),"")
    return p,s
def conforms(w):           # tiene prefijo Y sufijo reconocidos = encaja en la gramática de ranuras
    p,s=dec(w); return bool(p) and bool(s)

toks=[]  # (word, sec, locus_type)
cur=None
for raw in open("voy_lsi.txt",encoding="latin-1"):
    m=re.search(r"\$I=([A-Z])",raw)
    if m: cur=m.group(1)
    mm=re.match(r"^<f[0-9]+[rv][0-9]?\.[0-9]+,.([A-Za-z][A-Za-z0-9]*);H>\s+(.*)",raw)
    if not mm: continue
    typ,body=mm.group(1),mm.group(2)
    for w in re.split(r"[.,]",body.strip().rstrip("<->").strip()):
        w=w.strip()
        if w and w.isascii() and w.isalpha() and cur in SEC:
            toks.append((w.lower(),cur,typ[0]))

A=[(w,s) for w,s,_ in toks if conforms(w)]        # conformes
B=[(w,s) for w,s,_ in toks if not conforms(w)]    # no-conformes (el "residuo")
N=len(toks)
print(f"tokens con sección: {N}")
print(f"CONFORMES (encajan en ranuras): {len(A)} = {100*len(A)/N:.0f}%")
print(f"NO-CONFORMES (residuo):        {len(B)} = {100*len(B)/N:.0f}%\n")

# distribución global de secciones (referencia compartida)
glob_c=Counter(s for _,s,_ in toks)
Ng=sum(glob_c.values()); glob={s:glob_c[s]/Ng for s in glob_c}

def kl_spec(group, minf=3):
    wc=Counter(w for w,_ in group); wsec=defaultdict(Counter)
    for w,s in group: wsec[w][s]+=1
    num=den=0
    for w,cnt in wc.items():
        if cnt<minf: continue
        tot=sum(wsec[w].values()); kl=0
        for s,c in wsec[w].items():
            p=c/tot
            if p>0 and glob.get(s,0)>0: kl+=p*math.log2(p/glob[s])
        num+=cnt*kl; den+=cnt
    return num/den if den else 0, sum(1 for w,c in wc.items() if c>=minf)

def desc(group):
    wc=Counter(w for w,_ in group); n=len(group)
    return len(set(w for w,_ in group))/n, 100*sum(1 for c in wc.values() if c==1)/len(wc)  # TTR, hapax%

# nulo barajado (rompe la asociación palabra-sección) como piso de sesgo
import random; random.seed(3)
secs=[s for _,s,_ in toks]
def shuffled_kl(group_words):
    # reasignar secciones al azar a los MISMOS tokens del grupo
    gw=[w for w,_ in group_words]; rs=random.sample(secs,len(gw))
    return kl_spec(list(zip(gw,rs)))[0]

kaA,nA=kl_spec(A); kaB,nB=kl_spec(B)
flA=sum(shuffled_kl(A) for _ in range(5))/5; flB=sum(shuffled_kl(B) for _ in range(5))/5
ttrA,hxA=desc(A); ttrB,hxB=desc(B)
print(f"{'grupo':<16}{'KL-espec':>10}{'piso(azar)':>12}{'KL neta':>9}{'TTR':>7}{'hapax%':>8}{'tipos≥3':>9}")
print(f"{'CONFORMES':<16}{kaA:>10.3f}{flA:>12.3f}{kaA-flA:>9.3f}{ttrA:>7.2f}{hxA:>8.0f}{nA:>9}")
print(f"{'NO-CONFORMES':<16}{kaB:>10.3f}{flB:>12.3f}{kaB-flB:>9.3f}{ttrB:>7.2f}{hxB:>8.0f}{nB:>9}")

# ¿dónde viven? fracción en etiquetas (L) vs total
def label_share(pred):
    g=[t for t in toks if pred(t[0])]; lab=sum(1 for _,_,ty in g if ty=='L')
    return 100*lab/len(g)
print(f"\nfracción en ETIQUETAS: conformes {label_share(conforms):.1f}% · no-conformes {label_share(lambda w:not conforms(w)):.1f}%")
print("\nKTD: si NO-CONFORMES tiene KL neta MAYOR que conformes => el residuo carga más tema (sobrevive).")
print("     Si es menor o igual => el contenido NO está en el residuo (muere); son formas raras/irregulares.")
