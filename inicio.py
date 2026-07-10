#!/usr/bin/env python3
# La palabra inicial de linea: canto (metrica) / enfasis (prefijo anadido) / tono?
import re, collections, math

def load(path):
    # devuelve lista de lineas de PARRAFO: (kind, tokens); kind: 'para'|'line'
    out=[]; pend_kind=None; pend=[]
    def flush():
        if pend: out.append((pend_kind, pend[:]))
    for raw in open(path,encoding="latin-1"):
        m=re.match(r"<f[^;]*,([^;]);?[^;]*;H>\s*(.*)",raw)
        m=re.match(r"<f[^,;]*,(.)([A-Za-z])[^;]*;H>\s*(.*)",raw)
        if not m: continue
        sep,typ,body=m.group(1),m.group(2),m.group(3)
        if typ!="P":  # solo texto de parrafo (ignora etiquetas/radiales)
            continue
        toks=[w.replace("!","").replace("%","").replace("$","") for w in re.split(r"[.,]",body.strip().rstrip("<->").strip())]
        toks=[w for w in toks if w and "?" not in w and "*" not in w]
        if sep=="=":            # continuacion: pega al renglon previo
            if out: out[-1][1].extend(toks)
            elif pend: pend.extend(toks)
            continue
        flush(); pend=[]
        pend_kind = "para" if sep=="@" else "line"
        pend=toks
    flush()
    return out

lines=load("voy_lsi.txt")
para=[t for k,t in lines if k=="para" and t]
line=[t for k,t in lines if k=="line" and t]
allw=[w for _,t in lines for w in t]
wc=collections.Counter(allw)
TOP=set(w for w,_ in wc.most_common(40))
print(f"parrafos={len(para)}  lineas-internas={len(line)}  palabras={len(allw)}\n")

def firstglyph(words):
    c=collections.Counter(w[0] for w in words if w); t=sum(c.values())
    return [(g,round(v*100/t,1)) for g,v in c.most_common(6)]

para_first=[t[0] for t in para]
line_first=[t[0] for t in line]
mid=[w for _,t in lines for w in t[1:]]
print("1er glifo — INICIO DE PARRAFO (@P):", firstglyph(para_first))
print("1er glifo — inicio de linea (+P):  ", firstglyph(line_first))
print("1er glifo — resto (medio de linea):", firstglyph(mid))

# --- TEST ENFASIS: quitar 1er glifo -> ¿queda palabra comun? ---
def strip_hits(words):
    hit=0; tot=0
    for w in words:
        if len(w)<2: continue
        tot+=1
        if w[1:] in TOP: hit+=1
    return hit, tot, round(100*hit/tot,1) if tot else 0
print("\n[ENFASIS] quitar 1er glifo -> ¿el resto es una palabra del top-40?")
for name,ws in [("inicio de linea (+P)",line_first),("inicio de parrafo (@P)",para_first),("medio de linea",mid)]:
    h,t,p=strip_hits(ws); print(f"  {name:24}: {p}%  ({h}/{t})")
# ejemplos concretos
ej=[(w, w[1:]) for w in line_first if len(w)>1 and w[1:] in TOP]
print("  ejemplos:", ", ".join(f"{a}->{b}" for a,b in collections.Counter(ej).most_common(10)))

# --- TEST CANTO: regularidad metrica (long. de linea) ---
def stats(xs):
    m=sum(xs)/len(xs); sd=math.sqrt(sum((x-m)**2 for x in xs)/len(xs)); return m,sd,sd/m
print("\n[CANTO] regularidad de longitud de linea (CV bajo = metrico/verso)")
wl=[len(t) for t in line]           # palabras por linea interna
gl=[sum(len(w) for w in t) for t in line]  # glifos por linea
for lbl,xs in [("palabras/linea",wl),("glifos/linea",gl)]:
    m,sd,cv=stats(xs); print(f"  {lbl:16}: media={m:.1f}  sd={sd:.1f}  CV={cv:.2f}")

# --- TEST GALLOWS: ¿inicio favorece glifos ornamentales altos (k t p f)? ---
G=set("ktpf")
def gal(words):
    t=sum(1 for w in words if w); return round(100*sum(1 for w in words if w and w[0] in G)/t,1)
print("\n[ORNAMENTO] % que empieza con gallows (k/t/p/f, los glifos 'altos')")
print(f"  inicio de parrafo: {gal(para_first)}%   inicio de linea: {gal(line_first)}%   medio: {gal(mid)}%")
