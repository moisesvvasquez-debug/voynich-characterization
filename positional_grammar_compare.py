# -*- coding: utf-8 -*-
# ¿Que tan atado a la posicion esta cada glifo? I(glifo ; posicion S/M/E).
# Calibrar el Voynich (0.72) contra lenguas conocidas, sobre todo AGLUTINANTES
# (fin/hun) y CONSTRUIDA aglutinante (esperanto epo) = analogo de "lengua a priori".
import re, math, random, unicodedata
random.seed(7)

def posclass(i,L): return 'S' if i==0 else ('E' if i==L-1 else 'M')

def mi_pos(words):
    joint={}; g={}; c={}; N=0; lens=[]
    for w in words:
        L=len(w)
        if L<2: continue
        lens.append(L)
        for i,ch in enumerate(w):
            k=posclass(i,L)
            joint[(ch,k)]=joint.get((ch,k),0)+1
            g[ch]=g.get(ch,0)+1; c[k]=c.get(k,0)+1; N+=1
    if N==0: return None
    mi=0.0
    for (ch,k),n in joint.items():
        p=n/N
        mi+=p*math.log2(p/((g[ch]/N)*(c[k]/N)))
    return mi, N, len(g), (sum(lens)/len(lens))

def words_voynich():
    ws=[]
    for raw in open("voy_lsi.txt",encoding="latin-1"):
        m=re.match(r"^<f[0-9]+[rv][0-9]?\.[0-9]+,[^;]*;H>\s+(.*)",raw)
        if not m: continue
        for t in re.split(r"[.,]",m.group(1).strip()):
            t=t.strip()
            if t and t.isascii() and t.isalpha(): ws.append(t.lower())
    return ws

def words_file(path,enc="utf-8",strip_marks=True):
    try: txt=open(path,encoding=enc,errors="ignore").read().lower()
    except: return []
    if strip_marks:
        txt=''.join(ch for ch in unicodedata.normalize('NFD',txt)
                    if not unicodedata.combining(ch))
    # separar por cualquier no-letra (unicode-aware)
    ws=re.findall(r"[^\W\d_]+", txt, flags=re.UNICODE)
    return [w for w in ws if len(w)>=2]

def synth_numbers(length_dist,n=8000,base=20):
    ws=[]; lens=[x for x in length_dist if x>=2] or [4]
    for _ in range(n):
        L=random.choice(lens)
        digs=[random.randint(1,base-1)]+[random.randint(0,base-1) for _ in range(L-1)]
        ws.append(''.join(chr(ord('a')+d) for d in digs))
    return ws

V=words_voynich()

# set latino europeo (comparacion justa ~ mismo tipo de script), etiquetado por morfologia
LAT={
 "spn":"Español (fusional)","ita":"Italiano (fusional)","por":"Portugués (fusional)",
 "frn":"Francés (fusional)","lat":"Latín (fusional)","eng":"Inglés (analítico)",
 "ger":"Alemán (fusional)","swe":"Sueco (fusional)","dut":"Neerlandés (fusional)",
 "cze":"Checo (fusional)","fin":"Finés (AGLUTINANTE)","hun":"Húngaro (AGLUTINANTE)",
 "epo":"Esperanto (CONSTRUIDA aglut.)",
}
OTHER={"rus":"Ruso (cirílico)","grc":"Griego","heb":"Hebreo (abjad)",
       "far":"Farsi (abjad)","hin":"Hindi (devanagari)","tam":"Tamil"}

rows=[]
r=mi_pos(V); rows.append(("VOYNICH (EVA)",*r,"—"))
for code,label in LAT.items():
    ws=words_file(f"udhr/{code}.txt")
    r=mi_pos(ws)
    if r: rows.append((label,*r,"latino"))
Nums=synth_numbers([len(w) for w in V])
r=mi_pos(Nums); rows.append(("Números base-20 (control)",*r,"—"))

rows.sort(key=lambda x:-x[1])
print(f"{'sistema':<32}{'I(glifo;pos)':>13}{'tokens':>9}{'glifos':>8}{'|w|':>6}")
print("-"*68)
for label,mi,N,G,mlen,tag in rows:
    star=" *" if label.startswith("VOYNICH") else ""
    print(f"{label:<32}{mi:>13.3f}{N:>9}{G:>8}{mlen:>6.1f}{star}")

print("\n(referencia, otros scripts — NO comparables directo, abjad pierde vocales):")
for code,label in OTHER.items():
    ws=words_file(f"udhr/{code}.txt")
    r=mi_pos(ws)
    if r: print(f"  {label:<28}{r[0]:>10.3f}  ({r[2]} glifos, |w|={r[3]:.1f})")
