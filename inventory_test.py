# -*- coding: latin-1 -*-
# (1) Barrido AMPLIO de anclaje posicional I(glifo;pos) sobre TODAS las lenguas.
# (2) Test del modelo INVENTARIO del usuario: prefijo=clase/familia (seccion-dependiente),
#     nucleo=cualidad/augurio/adjetivo (deberia ser mas transversal a secciones).
import re, math, random, unicodedata, glob, os
from collections import Counter, defaultdict
random.seed(7)

def posclass(i,L): return 'S' if i==0 else ('E' if i==L-1 else 'M')
def mi_pos(words):
    j={}; g={}; c={}; N=0; lens=[]
    for w in words:
        L=len(w)
        if L<2: continue
        lens.append(L)
        for i,ch in enumerate(w):
            k=posclass(i,L); j[(ch,k)]=j.get((ch,k),0)+1
            g[ch]=g.get(ch,0)+1; c[k]=c.get(k,0)+1; N+=1
    if N==0: return None
    mi=sum((n/N)*math.log2((n/N)/((g[ch]/N)*(c[k]/N))) for (ch,k),n in j.items())
    return mi,N,len(g),sum(lens)/len(lens)

def latin_frac(words):
    tot=0; lat=0
    for w in words:
        for ch in w:
            tot+=1; lat+= ('a'<=ch<='z')
    return lat/tot if tot else 0

def words_file(path,strip=True):
    try: txt=open(path,encoding="utf-8",errors="ignore").read().lower()
    except: return []
    if strip:
        txt=''.join(ch for ch in unicodedata.normalize('NFD',txt) if not unicodedata.combining(ch))
    return [w for w in re.findall(r"[^\W\d_]+",txt,re.UNICODE) if len(w)>=2]

def words_voy():
    ws=[]
    for raw in open("voy_lsi.txt",encoding="latin-1"):
        m=re.match(r"^<f[0-9]+[rv][0-9]?\.[0-9]+,[^;]*;H>\s+(.*)",raw)
        if not m: continue
        for t in re.split(r"[.,]",m.group(1).strip()):
            t=t.strip()
            if t and t.isascii() and t.isalpha(): ws.append(t.lower())
    return ws

NAME={"spn":"Español","ita":"Italiano","por":"Portugués","frn":"Francés","lat":"Latín",
"eng":"Inglés","ger":"Alemán","swe":"Sueco","dut":"Neerlandés","cze":"Checo","fin":"Finés*",
"hun":"Húngaro*","epo":"Esperanto+","ind":"Indonesio","fil":"Filipino","jav":"Javanés",
"sun":"Sundanés","mli":"Maltés","rus":"Ruso","grc":"Griego","heb":"Hebreo","far":"Farsi",
"arz":"Árabe eg.","urd":"Urdu","hin":"Hindi","tam":"Tamil","chi":"Chino","chn":"Chino2","jpn":"Japonés"}

rows=[]
V=words_voy(); r=mi_pos(V); rows.append(("VOYNICH",r[0],r[1],r[2],r[3],1.0))
for f in sorted(glob.glob("udhr/*.txt")):
    code=os.path.splitext(os.path.basename(f))[0]
    ws=words_file(f); r=mi_pos(ws)
    if r and r[1]>800: rows.append((NAME.get(code,code),r[0],r[1],r[2],r[3],latin_frac(ws)))
# corpora grandes propios
for path,lab in [("quijote_es.txt","Español-Quijote"),("macer_latin.txt","Latín-Macer")]:
    ws=words_file(path); r=mi_pos(ws)
    if r: rows.append((lab,r[0],r[1],r[2],r[3],latin_frac(ws)))

rows.sort(key=lambda x:-x[1])
print("(1) ANCLAJE POSICIONAL  I(glifo;pos)  — *=aglutinante +=construida")
print(f"{'lengua':<18}{'I':>7}{'glifos':>8}{'|w|':>6}{'lat%':>6}  script")
for lab,mi,N,G,ml,lf in rows:
    sc = "latino" if lf>0.85 else ("mixto" if lf>0.4 else "no-latino")
    star=" <<<" if lab=="VOYNICH" else ""
    print(f"{lab:<18}{mi:>7.3f}{G:>8}{ml:>6.1f}{lf*100:>6.0f}  {sc}{star}")

# ================= (2) modelo INVENTARIO =================
print("\n(2) MODELO INVENTARIO: ¿prefijo=clase(seccion) y nucleo=cualidad(transversal)?")
SEC={"H","A","Z","B","C","P","S"}
PRE=["qok","qot","qo","cth","ckh","cph","cfh","ch","sh","ok","ot","yk","yt","yp","q","o","y","d","s"]
SUF=["aiin","aiir","ain","air","eedy","edy","eey","dy","ol","or","al","ar","am","an","in","ir","y","l","r","n"]
PRE.sort(key=len,reverse=True); SUF.sort(key=len,reverse=True)
def dec(w):
    p=next((x for x in PRE if w.startswith(x) and len(w)-len(x)>=1),"")
    rest=w[len(p):]
    s=next((x for x in SUF if rest.endswith(x) and len(rest)-len(x)>=1),"")
    core=rest[:len(rest)-len(s)] if s else rest
    return p or "0", core or "0", s or "0"
toks=[]; cur=None
for raw in open("voy_lsi.txt",encoding="latin-1"):
    m=re.search(r"\$I=([A-Z])",raw)
    if m: cur=m.group(1)
    mm=re.match(r"^<f[0-9]+[rv][0-9]?\.[0-9]+,[^;]*;H>\s+(.*)",raw)
    if not mm: continue
    for w in re.split(r"[.,]",mm.group(1).strip().rstrip("<->").strip()):
        w=w.strip()
        if w and w.isascii() and w.isalpha() and cur in SEC: toks.append((w.lower(),cur))
def MI(pairs):
    jj=Counter(pairs); a=Counter(x for x,_ in pairs); b=Counter(y for _,y in pairs); N=len(pairs)
    return sum((n/N)*math.log2((n/N)/((a[x]/N)*(b[y]/N))) for (x,y),n in jj.items())
def null_z(getter):
    obs=MI([(getter(w),s) for w,s in toks])
    secs=[s for _,s in toks]; vals=[getter(w) for w,_ in toks]; ns=[]
    for _ in range(150):
        random.shuffle(secs); ns.append(MI(list(zip(vals,secs))))
    mn=sum(ns)/len(ns); sd=(sum((x-mn)**2 for x in ns)/len(ns))**.5
    return obs,mn,(obs-mn)/sd if sd else 0
for lab,g in [("prefijo",lambda w:dec(w)[0]),("nucleo",lambda w:dec(w)[1]),("sufijo",lambda w:dec(w)[2])]:
    obs,mn,z=null_z(g)
    print(f"   MI({lab:<7};seccion)={obs:.4f}  nulo={mn:.4f}  z={z:+.0f}")
# ¿el mismo nucleo aparece en varias secciones? (transversalidad = cualidad/adjetivo)
core_secs=defaultdict(set); core_n=Counter()
for w,s in toks:
    c=dec(w)[1]; core_secs[c].add(s); core_n[c]+=1
freq_cores=[c for c,n in core_n.items() if n>=20]
multi=sum(1 for c in freq_cores if len(core_secs[c])>=4)
print(f"\n   nucleos frecuentes (n>=20): {len(freq_cores)}; presentes en >=4 de 7 secciones: {multi} ({100*multi/len(freq_cores):.0f}%)")
pre_secs=defaultdict(set); pre_n=Counter()
for w,s in toks:
    p=dec(w)[0]; pre_secs[p].add(s); pre_n[p]+=1
freq_pre=[p for p,n in pre_n.items() if n>=20]
multip=sum(1 for p in freq_pre if len(pre_secs[p])>=4)
print(f"   prefijos frecuentes (n>=20): {len(freq_pre)}; presentes en >=4 secciones: {multip} ({100*multip/len(freq_pre):.0f}%)")
print("   -> si nucleo transversal >> prefijo transversal, apoya: prefijo=clase, nucleo=valor")
