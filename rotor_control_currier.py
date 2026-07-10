#!/usr/bin/env python3
"""
CONTROL del test del rotor: ¿la deriva de SUFIJO sobrevive DENTRO de un solo dialecto Currier?
Confundido a descartar: el Voynich tiene lenguas Currier A y B ($L= en el encabezado).
Si A cae temprano y B tarde, el sufijo "derivaria" con la distancia sin ningun rotor.
Test justo: repetir la correlacion(similitud_sufijo, distancia_folio) restringido a $L=A y a $L=B
por separado, cada uno con su propia permutacion. Si sobrevive en al menos un dialecto homogeneo,
la deriva NO es artefacto del salto A->B.
"""
import re, math, collections, random
random.seed(0)
PATH="voy_lsi.txt"

lang={}; sec={}; words=collections.defaultdict(list); order=[]
for raw in open(PATH, encoding="latin-1"):
    h=re.match(r"^<(f[0-9]+[rv][0-9]?)>\s*<!\s*(.*)", raw)
    if h:
        fol,attrs=h.groups()
        mi=re.search(r"\$I=([A-Z])",attrs); ml=re.search(r"\$L=([A-Z])",attrs)
        sec[fol]=mi.group(1) if mi else None
        lang[fol]=ml.group(1) if ml else None
        continue
    m=re.match(r"^<(f[0-9]+[rv][0-9]?)\.[0-9]+,[^;]*;H>\s+(.*)", raw)
    if not m: continue
    fol,body=m.groups()
    if fol not in order: order.append(fol)
    for tok in re.split(r"[.,]", body.strip()):
        tok=re.sub(r"[!%?*\-<>@=\s]","",tok)
        if tok and len(tok)>=2: words[fol].append(tok)

def profile(fol):
    c=collections.Counter()
    for w in words[fol]: c[w[-2:]]+=1
    return c
def cosine(a,b):
    keys=set(a)|set(b); dot=sum(a[k]*b[k] for k in keys)
    na=math.sqrt(sum(v*v for v in a.values())); nb=math.sqrt(sum(v*v for v in b.values()))
    return dot/(na*nb) if na and nb else 0.0
def drift_corr(seq):
    profs={f:profile(f) for f in seq}; idx={f:i for i,f in enumerate(seq)}
    xs=[]; ys=[]
    for i in range(len(seq)):
        for j in range(i+1,len(seq)):
            xs.append(abs(idx[seq[i]]-idx[seq[j]])); ys.append(cosine(profs[seq[i]],profs[seq[j]]))
    n=len(xs); mx=sum(xs)/n; my=sum(ys)/n
    cov=sum((xs[k]-mx)*(ys[k]-my) for k in range(n))
    sx=math.sqrt(sum((v-mx)**2 for v in xs)); sy=math.sqrt(sum((v-my)**2 for v in ys))
    return (cov/(sx*sy) if sx and sy else 0.0), my

def run(seq,name):
    if len(seq)<12:
        print(f"\n[{name}] solo {len(seq)} folios — muestra chica, se omite"); return
    r_real,_=drift_corr(seq)
    nulls=[]
    for _ in range(1000):
        sh=seq[:]; random.shuffle(sh); nulls.append(drift_corr(sh)[0])
    mean=sum(nulls)/len(nulls); sd=math.sqrt(sum((x-mean)**2 for x in nulls)/len(nulls))
    z=(r_real-mean)/sd if sd else 0; p=sum(1 for x in nulls if x<=r_real)/len(nulls)
    print(f"\n[{name}]  n={len(seq)} folios")
    print(f"  corr(sim_sufijo, distancia) REAL={r_real:+.3f}  nulo {mean:+.3f}±{sd:.3f}  z={z:+.2f}  p={p:.3f}")
    print("  => "+("SOBREVIVE (deriva real dentro del dialecto)" if (p<0.05 and r_real<0) else "no significativo dentro del dialecto"))

HERB=[f for f in order if sec.get(f)=="H" and len(words[f])>=25]
byL=collections.Counter(lang.get(f) for f in HERB)
print(f"folios herbal: {len(HERB)}  por lengua Currier: {dict(byL)}")
run([f for f in HERB if lang.get(f)=="A"], "Currier A")
run([f for f in HERB if lang.get(f)=="B"], "Currier B")
