# -*- coding: utf-8 -*-
# Endurecer I(glifo ; posicion S/M/E): CI bootstrap + correccion de sesgo (piso barajado)
# + N COMUN (misma cantidad de palabras -> sesgo comparable) + control de LARGO (banda 4-7).
import re, math, random, unicodedata
random.seed(11)

def posclass(i,L): return 'S' if i==0 else ('E' if i==L-1 else 'M')
def mi(words):
    j={}; g={}; c={}; N=0
    for w in words:
        L=len(w)
        if L<2: continue
        for i,ch in enumerate(w):
            k=posclass(i,L); j[(ch,k)]=j.get((ch,k),0)+1
            g[ch]=g.get(ch,0)+1; c[k]=c.get(k,0)+1; N+=1
    if N==0: return 0.0
    return sum((n/N)*math.log2((n/N)/((g[ch]/N)*(c[k]/N))) for (ch,k),n in j.items())

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
    txt=''.join(ch for ch in unicodedata.normalize('NFD',txt) if not unicodedata.combining(ch))
    return [w for w in re.findall(r"[^\W\d_]+",txt,re.UNICODE) if len(w)>=2]
def synth(lendist,n=40000,base=20):
    lens=[x for x in lendist if x>=2] or [4]; out=[]
    for _ in range(n):
        L=random.choice(lens); out.append(''.join(chr(ord('a')+random.randint(0,base-1)) for _ in range(L)))
    return out

V=words_voy()
corp={
 "VOYNICH":V,
 "Español":words_file("quijote_es.txt"),
 "Finés*":words_file("udhr/fin.txt"),
 "Latín":words_file("macer_latin.txt"),
 "Números b20":synth([len(w) for w in V]),
}
NCOMMON=min(12000, min(len(w) for w in corp.values()))
print(f"N común = {NCOMMON} palabras por corpus (sesgo comparable)\n")
print(f"{'corpus':<14}{'MI obs':>8}{'piso(barajado)':>15}{'MI corregida':>14}{'IC95%':>18}{'MI |len4-7':>12}")
for name,ws in corp.items():
    ws=[w for w in ws if len(w)>=2]
    samp=random.sample(ws, NCOMMON)
    obs=mi(samp)
    # piso: barajar clase de posicion es equivalente a romper asociacion -> shuffle de palabras no sirve;
    # el piso de sesgo = MI de datos con posiciones aleatorizadas: reasignar cada glifo a S/M/E al azar
    def shuffled_once(sample):
        # reconstituir "palabras" con mismos glifos pero clases al azar: medimos MI con clase aleatoria
        flat=[(ch, posclass(i,len(w))) for w in sample for i,ch in enumerate(w) if len(w)>=2]
        glyphs=[a for a,_ in flat]; classes=[b for _,b in flat]
        random.shuffle(classes)
        j={}; g={}; c={}; N=len(glyphs)
        for a,b in zip(glyphs,classes):
            j[(a,b)]=j.get((a,b),0)+1; g[a]=g.get(a,0)+1; c[b]=c.get(b,0)+1
        return sum((n/N)*math.log2((n/N)/((g[a]/N)*(c[b]/N))) for (a,b),n in j.items())
    floor=sum(shuffled_once(samp) for _ in range(60))/60
    # bootstrap CI
    boots=[]
    for _ in range(300):
        bs=[samp[random.randrange(NCOMMON)] for _ in range(NCOMMON)]
        boots.append(mi(bs))
    boots.sort(); lo=boots[int(.025*len(boots))]; hi=boots[int(.975*len(boots))]
    # length-matched 4-7
    lm=[w for w in ws if 4<=len(w)<=7]
    lm=random.sample(lm, min(NCOMMON,len(lm))) if len(lm)>=2 else []
    milm=mi(lm) if lm else float('nan')
    print(f"{name:<14}{obs:>8.3f}{floor:>15.3f}{obs-floor:>14.3f}{('['+format(lo,'.3f')+','+format(hi,'.3f')+']'):>18}{milm:>12.3f}")
print("\nMI corregida = MI obs − piso de sesgo (posiciones aleatorizadas). IC95% por bootstrap (300).")
print("Si el IC de VOYNICH no se solapa con el del resto y sigue arriba a len 4-7 = robusto.")
