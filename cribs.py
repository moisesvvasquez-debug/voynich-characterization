#!/usr/bin/env python3
# Ataque estilo Bletchley: inicios/finales (gramatica de palabra),
# posicion de linea (LAAFU), colocaciones y frases candidatas (cribs).
import re, collections

def load_lines(path):
    lines=[]; cur_sec=None
    for raw in open(path,encoding="latin-1"):
        if raw.startswith("<") and "$I=" in raw:
            m=re.search(r"\$I=([A-Z])",raw); cur_sec=m.group(1) if m else None
        m=re.match(r"<[^>]*;H>\s*(.*)",raw)
        if not m: continue
        body=m.group(1).strip().rstrip("<->").strip()
        toks=[w.replace("!","").replace("%","") for w in re.split(r"[.,]",body)]
        toks=[w for w in toks if w and "?" not in w and "*" not in w]
        if toks: lines.append((cur_sec,toks))
    return lines

lines=load_lines("voy_lsi.txt")
allwords=[w for _,ts in lines for w in ts]
N=len(allwords)
print(f"lineas={len(lines)}  palabras={N}\n")

def topfix(words, k, end=False):
    c=collections.Counter()
    for w in words:
        seg = w[-k:] if end else w[:k]
        if len(w)>=k: c[seg]+=1
    return c

print("=== INICIOS de palabra (todo el corpus, ponderado por token) ===")
for k in (1,2,3):
    top=topfix(allwords,k).most_common(8)
    print(f"  {k}-grama inicial:", ", ".join(f"{s}·{v*100//N}%" for s,v in top))
print("=== FINALES de palabra ===")
for k in (1,2,3):
    top=topfix(allwords,k,end=True).most_common(8)
    print(f"  {k}-grama final:  ", ", ".join(f"{s}·{v*100//N}%" for s,v in top))

print("\n=== POSICION DE LINEA (LAAFU) — ¿la 1a palabra es especial? ===")
first=[ts[0] for _,ts in lines]
rest=[w for _,ts in lines for w in ts[1:]]
def initdist(words):
    c=collections.Counter(w[0] for w in words if w); t=len(words)
    return {s:round(v*100/t,1) for s,v in c.most_common(6)}
print("  1er glifo, palabra INICIAL de linea:", initdist(first))
print("  1er glifo, resto de palabras:       ", initdist(rest))
lastw=[ts[-1] for _,ts in lines]
def enddist(words):
    c=collections.Counter(w[-1] for w in words if w); t=len(words)
    return {s:round(v*100/t,1) for s,v in c.most_common(6)}
print("  ult glifo, palabra FINAL de linea:  ", enddist(lastw))
print("  ult glifo, resto:                   ", enddist([w for _,ts in lines for w in ts[:-1]]))

print("\n=== PALABRAS mas frecuentes ===")
wc=collections.Counter(allwords)
print("  global:", ", ".join(f"{w}·{c}" for w,c in wc.most_common(12)))
fc=collections.Counter(first)
print("  como INICIO de linea:", ", ".join(f"{w}·{c}" for w,c in fc.most_common(10)))

print("\n=== COLOCACIONES (bigramas dentro de linea) ===")
big=collections.Counter()
for _,ts in lines:
    for a,b in zip(ts,ts[1:]): big[(a,b)]+=1
print("  top bigramas:")
for (a,b),c in big.most_common(15):
    print(f"    {a} {b}  ·{c}")

print("\n=== FRASES candidatas (trigramas repetidos = posibles formulas) ===")
tri=collections.Counter()
for _,ts in lines:
    for a,b,cc in zip(ts,ts[1:],ts[2:]): tri[(a,b,cc)]+=1
for (a,b,cc),c in tri.most_common(10):
    print(f"    {a} {b} {cc}  ·{c}")
