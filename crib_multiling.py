# -*- coding: utf-8 -*-
# Idea usuario: ¿los morfemas Voynich (grado caliente/tibio/frío, o "vegetal")
# coinciden con palabras reales en algún idioma? -> HONESTO: contar coincidencias,
# pero contra un NULO de morfemas aleatorios. Si Voynich no supera al azar = casualidad.
import random, itertools
random.seed(7)

# palabras reales (romanizadas) para caliente/tibio/frío/planta en ~12 lenguas
TARGETS = {
 "caliente": ["calidus","caldo","caliente","chaud","harr","thermos","cham","garm","ushna","re","atsui","hot","warm","heiss"],
 "tibio":    ["tepidus","tiepido","tibio","tiede","fatir","chliaros","posher","lukewarm","mand"],
 "frio":     ["frigidus","freddo","frio","froid","bard","psychros","qar","sard","shita","leng","samui","cold","kalt"],
 "planta":   ["planta","herba","erba","plante","nabat","botane","esev","giyah","osadhi","zhiwu","shokubutsu","vegetal","kraut","phyton"],
}
ALLWORDS = [(w,cat) for cat,ws in TARGETS.items() for w in ws]

# morfemas Voynich a probar: grados (sufijos) + dominio/herbal frecuentes
VOY = {
 "grado":  ["y","dy","edy","eey","ol","or","aiin","al","ar","in"],
 "vegetal":["chol","chor","daiin","dain","chedy","shedy","okaiin","otaiin","qokeedy","cthy"],
}
VOY_ALL = VOY["grado"]+VOY["vegetal"]

VOWELS=set("aeiouy")
def cons(s): return "".join(c for c in s.lower() if c not in VOWELS)
def lev(a,b):
    if abs(len(a)-len(b))>1: return 9
    prev=list(range(len(b)+1))
    for i,ca in enumerate(a,1):
        cur=[i]
        for j,cb in enumerate(b,1):
            cur.append(min(prev[j]+1,cur[-1]+1,prev[j-1]+(ca!=cb)))
        prev=cur
    return prev[-1]
def matches(morph, word):
    a,b=morph.lower(),word.lower()
    if lev(a,b)<=1: return True
    ca,cb=cons(a),cons(b)
    if ca and ca==cb: return True
    if len(ca)>=2 and ca in cb: return True
    if len(cb)>=2 and cb in ca: return True
    return False

def count_hits(morphs):
    hits=0; ex=[]
    for m in morphs:
        for w,cat in ALLWORDS:
            if matches(m,w):
                hits+=1; ex.append((m,w,cat))
    return hits, ex

obs, examples = count_hits(VOY_ALL)
print(f"morfemas Voynich probados: {len(VOY_ALL)}  |  palabras-objetivo: {len(ALLWORDS)} en ~12 lenguas")
print(f"COINCIDENCIAS Voynich (criterio generoso): {obs}")
print("  ejemplos de 'coincidencias' encontradas:")
for m,w,cat in examples[:12]:
    print(f"    {m:<9} ~ {w:<12} ({cat})")

# NULO: morfemas aleatorios con mismas longitudes e inventario de glifos Voynich
INV=list("qokeydainlrchst")
lens=[len(m) for m in VOY_ALL]
nulls=[]
for _ in range(2000):
    rand=[ "".join(random.choice(INV) for _ in range(L)) for L in lens ]
    nulls.append(count_hits(rand)[0])
mu=sum(nulls)/len(nulls); sd=(sum((x-mu)**2 for x in nulls)/len(nulls))**.5
z=(obs-mu)/sd if sd else 0
p_ge=sum(1 for x in nulls if x>=obs)/len(nulls)
print(f"\nNULO (morfemas aleatorios, 2000 corridas): media={mu:.1f} ± {sd:.1f}")
print(f"Voynich={obs}  z={z:+.2f}  P(azar >= Voynich)={p_ge:.2f}")
print("  -> si z~0 y p alto: las coincidencias son las MISMAS que da el azar = casualidad, NO señal")
