# -*- coding: latin-1 -*-
# KTD: ¿los glifos se comportan como DÍGITOS de un sistema posicional (cualquiera
# en cualquier posición) o como LETRAS/morfemas atados a su posición?
# Discriminador: informacion mutua I(glifo ; clase_de_posicion S/M/E).
#   numeros posicionales  -> I ~ 0  (dígito libre)
#   morfologia (lenguas)  -> I alto (letras especializadas por posicion)
import re, math, random, unicodedata
random.seed(7)

def posclass(i, L):
    if i == 0: return 'S'
    if i == L-1: return 'E'
    return 'M'

def mi_glyph_position(words):
    joint = {}   # (g,c) -> n
    gcount = {}; ccount = {}; N = 0
    for w in words:
        L = len(w)
        if L < 2:            # length-1 ambiguas (inicio=final): se omiten
            continue
        for i, g in enumerate(w):
            c = posclass(i, L)
            joint[(g,c)] = joint.get((g,c),0)+1
            gcount[g] = gcount.get(g,0)+1
            ccount[c] = ccount.get(c,0)+1
            N += 1
    mi = 0.0
    for (g,c),n in joint.items():
        pgc = n/N; pg = gcount[g]/N; pc = ccount[c]/N
        mi += pgc*math.log2(pgc/(pg*pc))
    return mi, N, len(gcount)

# ---------- fuentes ----------
def words_voynich():
    ws=[]
    for raw in open("voy_lsi.txt",encoding="latin-1"):
        m=re.match(r"^<f[0-9]+[rv][0-9]?\.[0-9]+,[^;]*;H>\s+(.*)",raw)
        if not m: continue
        for t in re.split(r"[.,]", m.group(1).strip()):
            t=t.strip()
            if t and t.isascii() and t.isalpha(): ws.append(t.lower())
    return ws

def words_from_text(path):
    txt=open(path,encoding="latin-1").read().lower()
    txt=''.join(c if (c.isalpha() or c.isspace()) else ' '
                for c in unicodedata.normalize('NFD',txt)
                if not unicodedata.combining(c))
    return [w for w in txt.split() if len(w)>=2]

def synthetic_numbers(length_dist, n=8000, base=20):
    # numeros base-20: primer digito 1..base-1, resto 0..base-1 -> letra a..
    ws=[]
    lens=list(length_dist)
    for _ in range(n):
        L=random.choice(lens)
        if L<2: L=2
        digs=[random.randint(1,base-1)]+[random.randint(0,base-1) for _ in range(L-1)]
        ws.append(''.join(chr(ord('a')+d) for d in digs))
    return ws

V=words_voynich()
E=words_from_text("quijote_es.txt")
La=words_from_text("macer_latin.txt")
Vlens=[len(w) for w in V if len(w)>=2]
Nums=synthetic_numbers(Vlens)

print(f"{'fuente':<26}{'I(glifo;pos) bits':>18}{'tokens':>10}{'glifos':>8}")
for name,ws in [("VOYNICH (EVA, Takahashi)",V),
                ("Español (Quijote)",E),
                ("Latín (Macer)",La),
                ("Números base-20 (control)",Nums)]:
    mi,N,G=mi_glyph_position(ws)
    print(f"{name:<26}{mi:>18.4f}{N:>10}{G:>8}")

# ---------- ejemplos de especializacion posicional en Voynich ----------
print("\nGlifos Voynich mas atados a una posicion (P(S) o P(E) dominante):")
from collections import Counter, defaultdict
pos=defaultdict(Counter)
for w in V:
    L=len(w)
    if L<2: continue
    for i,g in enumerate(w): pos[g][posclass(i,L)]+=1
rows=[]
for g,cnt in pos.items():
    tot=sum(cnt.values())
    if tot<200: continue
    pS,pM,pE=cnt['S']/tot,cnt['M']/tot,cnt['E']/tot
    skew=max(pS,pE)                      # que tan dominante es un extremo
    rows.append((skew,g,pS,pM,pE,tot))
rows.sort(reverse=True)
print(f"  {'glifo':<6}{'P(inicio)':>10}{'P(medio)':>10}{'P(final)':>10}{'n':>8}")
for skew,g,pS,pM,pE,tot in rows[:8]:
    print(f"  {g:<6}{pS:>10.2f}{pM:>10.2f}{pE:>10.2f}{tot:>8}")
