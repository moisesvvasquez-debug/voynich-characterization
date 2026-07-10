# -*- coding: utf-8 -*-
# KTD #1: ¿la ABREVIACIÓN medieval del latín reproduce el perfil Voynich
# (h2 baja + estructura de ranuras)? Modelo de braquigrafía sobre latín normal.
# NOTA: el modelo de abreviación es un PRIOR construido, no data real; sirve para
# ver la DIRECCIÓN del efecto, no como prueba absoluta.
import re, math, unicodedata
from collections import Counter

def h2(words):                       # H(char siguiente | char previo), bits, sobre stream con espacios
    s=" ".join(words)
    bi=Counter(zip(s,s[1:])); uni=Counter(s); N=sum(bi.values()); H=0.0
    for (a,b),n in bi.items():
        H -= (n/N)*math.log2(n/uni[a])
    return H

def template_cov(words, k=15):       # % de palabras con inicio-2glifos y final-2glifos ambos en top-k
    pre=Counter(w[:2] for w in words if len(w)>=2); suf=Counter(w[-2:] for w in words if len(w)>=2)
    tp=set(x for x,_ in pre.most_common(k)); ts=set(x for x,_ in suf.most_common(k))
    ok=sum(1 for w in words if len(w)>=2 and w[:2] in tp and w[-2:] in ts)
    return 100*ok/len(words)

def trip_rep(words):                 # % de trigramas-de-palabra que se repiten
    tr=Counter(tuple(words[i:i+3]) for i in range(len(words)-2))
    return 100*sum(1 for n in tr.values() if n>1)/max(1,len(tr))

def stats(name, words):
    words=[w for w in words if w]
    ml=sum(len(w) for w in words)/len(words)
    ttr=len(set(words))/len(words)
    print(f"{name:<26}{h2(words):>7.2f}{ml:>7.2f}{ttr:>7.2f}{template_cov(words):>9.1f}{trip_rep(words):>9.1f}{len(words):>9}")

# ---------- corpora ----------
def words_file(path):
    txt=open(path,encoding="utf-8",errors="ignore").read().lower()
    txt=''.join(c for c in unicodedata.normalize('NFD',txt) if not unicodedata.combining(c))
    return [w for w in re.findall(r"[a-z]+",txt) if len(w)>=1]

def words_voy():
    ws=[]
    for raw in open("voy_lsi.txt",encoding="latin-1"):
        m=re.match(r"^<f[0-9]+[rv][0-9]?\.[0-9]+,[^;]*;H>\s+(.*)",raw)
        if not m: continue
        for t in re.split(r"[.,]",m.group(1).strip()):
            t=t.strip()
            if t and t.isascii() and t.isalpha(): ws.append(t.lower())
    return ws

# ---------- modelo de abreviación medieval (braquigrafía) ----------
WHOLE={"et":"&","est":"ē","non":"n","enim":"ñ","autem":"a","quod":"qd","qui":"q",
       "quae":"q","quam":"q","sunt":"s","per":"p","pro":"p","atque":"aq","sed":"s",
       "cum":"c","tamen":"t","sicut":"sic","vero":"v","ergo":"g","igitur":"ig"}
END=[("orum","ꝛ"),("arum","ꝛ"),("erum","ꝛ"),("ibus","b"),("atur","~"),("etur","~"),
     ("itur","~"),("tur","~"),("bus","b"),("rum","ꝛ"),("que","q"),("us","ꝰ"),("um","ũ"),
     ("is","ꝭ"),("es","ę"),("as","ą")]
PRE=[("con","ↄ"),("com","ↄ"),("per","p"),("pro","p"),("prae","p")]
def abbrev(w):
    if w in WHOLE: return WHOLE[w]
    for a,b in PRE:                          # prefijo
        if w.startswith(a) and len(w)>len(a)+1: w=b+w[len(a):]; break
    for a,b in END:                          # terminación (una)
        if w.endswith(a) and len(w)>len(a)+1: w=w[:-len(a)]+b; break
    w=re.sub(r"([aeiou])[mn](?=[bcdfghjklpqrstvxz])","\\1̄",w)   # nasal interna -> barra
    w=re.sub(r"[mn]$","",w)                                       # nasal final cae
    if len(w)>6: w=w[:4]+"·"                                      # suspensión de palabra larga
    return w

# ---------- correr ----------
V=words_voy()
LA=words_file("macer_latin.txt")
ES=words_file("quijote_es.txt")[:len(LA)]
LA_ab=[abbrev(w) for w in LA]

print(f"{'corpus':<26}{'h2':>7}{'|w|':>7}{'TTR':>7}{'ranuras%':>9}{'trip%':>9}{'N':>9}")
print("-"*74)
stats("VOYNICH", V)
stats("Latín (Macer) crudo", LA)
stats("Latín ABREVIADO (modelo)", LA_ab)
stats("Español (ref)", ES)
print("\nejemplos de abreviación:")
for w in ["dominus","omnium","tantum","virtutem","herbarum","conservat","proprietas","calidus","frigidum"]:
    print(f"   {w:<12}-> {abbrev(w)}")
print("\nKTD: si 'Latín abreviado' se ACERCA a Voynich en h2 y ranuras% => la abreviación")
print("     es una explicación viable de la anomalía (sin necesitar generador).")
