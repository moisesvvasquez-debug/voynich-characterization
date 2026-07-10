#!/usr/bin/env python3
"""
TEST DEL ROTOR DESLIZANTE (idea del usuario).
Hipotesis: la "configuracion" (inventario de afijos = ajuste del dial) NO es fija:
se desplaza a lo largo del manuscrito como un rotor que avanza. Firma esperada:
folios VECINOS comparten ajuste (perfil de prefijos parecido) y folios LEJANOS divergen.
=> la similitud de perfil DECAE con la distancia de folio, por encima del azar.

Metodo: perfil de prefijos y sufijos por folio (Takahashi ;H) -> similitud coseno par a par
-> correlacion(similitud, distancia_de_folio) real vs 1000 barajados del orden de folios.
Solo lengua/texto, $0. Baseline honesto (permutacion).
"""
import re, math, collections, random
random.seed(0)
PATH="voy_lsi.txt"

# 1) parsear: seccion por folio ($I=) y palabras por folio (transcriptor Takahashi ;H)
sec={}                         # folio -> letra de illustration-type ($I)
words=collections.defaultdict(list)  # folio -> [tokens]
order=[]                       # orden de aparicion = orden del manuscrito
for raw in open(PATH, encoding="latin-1"):
    h=re.match(r"^<(f[0-9]+[rv][0-9]?)>\s*<!\s*\$I=([A-Z])", raw)
    if h:
        sec[h.group(1)]=h.group(2); continue
    m=re.match(r"^<(f[0-9]+[rv][0-9]?)\.[0-9]+,[^;]*;H>\s+(.*)", raw)
    if not m: continue
    fol,body=m.groups()
    if fol not in order: order.append(fol)
    for tok in re.split(r"[.,]", body.strip()):
        tok=re.sub(r"[!%?*\-<>@=\s]","",tok)
        if tok and len(tok)>=2: words[fol].append(tok)

# 2) quedarnos con folios HERBAL ($I=H) con suficiente texto
HERB=[f for f in order if sec.get(f)=="H" and len(words[f])>=25]
print(f"folios herbal con >=25 palabras: {len(HERB)}  (orden real del manuscrito)")

def profile(fol, which):
    c=collections.Counter()
    for w in words[fol]:
        aff = w[:2] if which=="pre" else w[-2:]
        c[aff]+=1
    return c

def cosine(a,b):
    keys=set(a)|set(b);
    dot=sum(a[k]*b[k] for k in keys)
    na=math.sqrt(sum(v*v for v in a.values())); nb=math.sqrt(sum(v*v for v in b.values()))
    return dot/(na*nb) if na and nb else 0.0

def drift_corr(seq, which):
    """correlacion Pearson entre similitud de perfil y distancia de indice en 'seq'."""
    profs={f:profile(f,which) for f in seq}
    idx={f:i for i,f in enumerate(seq)}
    xs=[]; ys=[]
    for i in range(len(seq)):
        for j in range(i+1,len(seq)):
            xs.append(abs(idx[seq[i]]-idx[seq[j]]))
            ys.append(cosine(profs[seq[i]],profs[seq[j]]))
    n=len(xs); mx=sum(xs)/n; my=sum(ys)/n
    cov=sum((xs[k]-mx)*(ys[k]-my) for k in range(n))
    sx=math.sqrt(sum((v-mx)**2 for v in xs)); sy=math.sqrt(sum((v-my)**2 for v in ys))
    r = cov/(sx*sy) if sx and sy else 0.0
    # tambien: similitud media de vecinos (|d|=1) vs global
    adj=[ys[k] for k in range(n) if xs[k]==1];
    return r, (sum(adj)/len(adj) if adj else 0), my

for which in ("pre","suf"):
    r_real,adj_real,glob = drift_corr(HERB, which)
    # permutacion: barajar el orden de folios, recomputar r
    nulls=[]
    for _ in range(1000):
        sh=HERB[:]; random.shuffle(sh)
        nulls.append(drift_corr(sh, which)[0])
    nulls.sort()
    # p-value 1-cola: rotor => r NEGATIVO fuerte (similitud baja con distancia)
    p = sum(1 for x in nulls if x<=r_real)/len(nulls)
    mean_null=sum(nulls)/len(nulls)
    sd=math.sqrt(sum((x-mean_null)**2 for x in nulls)/len(nulls))
    z=(r_real-mean_null)/sd if sd else 0
    label = "pre (prefijo)" if which=="pre" else "suf (sufijo)"
    print(f"\n=== {label} ===")
    print(f"corr(similitud, distancia_folio) REAL = {r_real:+.3f}   (negativo = decae con distancia = rotor)")
    print(f"nulo barajado: media {mean_null:+.3f}  sd {sd:.3f}   z={z:+.2f}   p(1-cola)={p:.3f}")
    print(f"similitud media VECINOS(|d|=1) = {adj_real:.3f}   vs GLOBAL = {glob:.3f}   (mayor en vecinos = rotor)")
    veredicto = "SEÑAL DE ROTOR (deriva real)" if (p<0.05 and r_real<0) else "SIN deriva por encima del azar"
    print(f"VEREDICTO: {veredicto}")
