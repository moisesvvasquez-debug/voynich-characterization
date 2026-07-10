#!/usr/bin/env python3
"""
PASO 1 del test de ETIQUETAS (crib con referente tight). Solo texto, $0.
Extrae de la transliteración TODOS los tokens de tipo ETIQUETA (locus @L..;H = label),
por folio, los descompone en el dial (prefijo·núcleo·sufijo) y reporta:
  - folios ricos en etiquetas (candidatos: farmacéutica f88-f102, zodiaco f70-f73)
  - si las etiquetas son combinatorias como los párrafos (mismo inventario de afijos?)
  - inventario de sufijos/prefijos de etiquetas para el cruce posterior con visión.
Salida: consola + labels.json (folio -> [ {word, pre, core, suf, line, idx_en_linea} ] en orden de lectura).
"""
import re, json, collections

PRE=["qok","qot","qol","qo","ok","ot","op","o","cth","ckh","ch","sh","d","s","y","l","r","k","t","p","f","a"]
SUF=["aiin","aiiin","ain","iin","eedy","eeey","eey","eody","edy","ody","ey","dy","ol","or","al","ar","am","in","y","s","o","d","l","r","n"]
def dec(w):
    core=w;pre="";suf=""
    for p in PRE:
        if core.startswith(p) and len(core)>len(p): pre=p;core=core[len(p):];break
    for s in SUF:
        if core.endswith(s) and len(core)>len(s): suf=s;core=core[:-len(s)];break
    return (pre,core,suf) if pre and suf else None

sec={}
labels=collections.defaultdict(list)   # folio -> lista de etiquetas en orden
para_words=collections.Counter()       # afijos de párrafos (para comparar)
label_words=collections.Counter()
for raw in open("voy_lsi.txt",encoding="latin-1"):
    h=re.match(r"^<(f[0-9]+[rv][0-9]?)>\s*<!\s*\$I=([A-Z])",raw)
    if h: sec[h.group(1)]=h.group(2); continue
    m=re.match(r"^<(f[0-9]+[rv][0-9]?)\.([0-9]+),.([A-Za-z][A-Za-z0-9]*);H>\s+(.*)",raw)
    if not m: continue
    fol,line,typ,body=m.groups()
    toks=[re.sub(r"[!%?*\-<>@=\s]","",t) for t in re.split(r"[.,]",body.strip())]
    toks=[t for t in toks if t and len(t)>=2 and "?" not in t and "*" not in t]
    if typ[0]=="L":   # etiqueta
        for i,t in enumerate(toks):
            labels[fol].append({"word":t,"line":int(line),"idx":i,"dec":dec(t)})
            label_words[t]+=1
    elif typ[0]=="P": # párrafo
        for t in toks: para_words[t]+=1

# folios ricos en etiquetas
rich=sorted(labels.items(), key=lambda kv:-len(kv[1]))
print("=== FOLIOS con más etiquetas (candidatos al test) ===")
for fol,ls in rich[:20]:
    print(f"  {fol:7} sección={sec.get(fol,'?')}  {len(ls):3} etiquetas   ej: {[l['word'] for l in ls[:5]]}")
tot=sum(len(v) for v in labels.values())
print(f"\nTOTAL etiquetas (label-loci) en el manuscrito: {tot} en {len(labels)} folios")

# ¿son combinatorias como los párrafos?
def frac_dec(counter):
    n=sum(counter.values()); d=sum(c for w,c in counter.items() if dec(w)); return d,n
ld,ln=frac_dec(label_words); pd,pn=frac_dec(para_words)
print(f"\n¿etiquetas combinatorias? se descomponen {100*ld/ln:.0f}% de etiquetas vs {100*pd/pn:.0f}% de palabras de párrafo")
# inventario de afijos de etiquetas
lp=collections.Counter(); ls_=collections.Counter()
for w in label_words:
    d=dec(w)
    if d: lp[d[0]]+=label_words[w]; ls_[d[2]]+=label_words[w]
print("prefijos de etiqueta (top):", lp.most_common(8))
print("sufijos de etiqueta (top):", ls_.most_common(8))

json.dump({fol:ls for fol,ls in labels.items()}, open("labels.json","w"))
print("\n-> labels.json escrito (etiquetas por folio, en orden de lectura)")
