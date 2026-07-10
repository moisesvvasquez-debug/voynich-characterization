# -*- coding: utf-8 -*-
# Exploración KTD autónoma: correr tests decisivos, detenerse si algo SOBREVIVE.
import re, math, bz2, random, unicodedata
from collections import Counter, defaultdict
random.seed(5)

def words_voy():
    ws=[]
    for raw in open("voy_lsi.txt",encoding="latin-1"):
        m=re.match(r"^<f[0-9]+[rv][0-9]?\.[0-9]+,[^;]*;H>\s+(.*)",raw)
        if not m: continue
        for t in re.split(r"[.,]",m.group(1).strip()):
            t=t.strip()
            if t and t.isascii() and t.isalpha(): ws.append(t.lower())
    return ws
def words_file(path):
    txt=open(path,encoding="utf-8",errors="ignore").read().lower()
    txt=''.join(c for c in unicodedata.normalize('NFD',txt) if not unicodedata.combining(c))
    return [w for w in re.findall(r"[a-z]+",txt) if w]

V=words_voy(); ES=words_file("quijote_es.txt"); LA=words_file("macer_latin.txt")
n=min(len(V),len(ES),len(LA)); V,ES,LA=V[:n],ES[:n],LA[:n]
Vsh=V[:]; random.shuffle(Vsh)                          # orden de palabra destruido
uni=Counter(V); pool=list(uni.elements())
Viid=[pool[random.randrange(len(pool))] for _ in range(n)]  # generador i.i.d. (misma freq)

def comp_ratio(words):
    b=(" ".join(words)).encode("utf-8"); return len(bz2.compress(b,9))/len(b)

print("=== TEST 1: COMPRESIÓN (bz2) — razón comprimido/original (menor = más estructura) ===")
for name,w in [("VOYNICH",V),("Voynich BARAJADO",Vsh),("Voynich i.i.d. (generador)",Viid),
               ("Español",ES),("Latín",LA)]:
    print(f"  {name:<28}{comp_ratio(w):.4f}")
print("  KTD: si Voynich ≈ su i.i.d. y ≈ barajado -> sin estructura extra al unigrama (inclina a mecanismo).")

def cross_entropy(words, alpha=0.1):
    cut=int(.8*len(words)); tr,te=words[:cut],words[cut:]
    uni=Counter(tr); N=len(tr); V=len(uni)
    bi=defaultdict(Counter)
    for a,b in zip(tr,tr[1:]): bi[a][b]+=1
    Hu=Hb=0.0; prev=None
    for w in te:
        pu=(uni[w]+alpha)/(N+alpha*(V+1)); Hu-=math.log2(pu)
        if prev is not None and prev in bi:
            c=bi[prev]; tot=sum(c.values()); pb=(c[w]+alpha)/(tot+alpha*(V+1))
        else: pb=pu
        Hb-=math.log2(pb); prev=w
    return Hu/len(te), Hb/len(te)

print("\n=== TEST 2: MEMORIA SECUENCIAL — entropía por palabra held-out (unigrama vs bigrama) ===")
print("  (mejora = cuánta info aporta la palabra ANTERIOR = estructura de orden)")
for name,w in [("VOYNICH",V),("Español",ES),("Latín",LA),("Voynich i.i.d.",Viid),("Voynich barajado",Vsh)]:
    Hu,Hb=cross_entropy(w); print(f"  {name:<20} unigrama {Hu:5.2f}  bigrama {Hb:5.2f}  mejora {Hu-Hb:5.2f} bits")
print("  KTD: si la MEJORA del Voynich << la de una lengua real -> poco orden secuencial (inclina a mecanismo/lista).")
print("       si la MEJORA fuera GRANDE (como lengua) -> habría memoria de palabra = SORPRESA, valioso.")
