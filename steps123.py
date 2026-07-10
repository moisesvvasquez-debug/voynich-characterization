#!/usr/bin/env python3
# Pasos 2da capa: (1) memoria de largo alcance (MI vs distancia),
# (2) especificidad semantica por seccion (KL vs nulo barajado),
# (3) direccionalidad (h2 adelante vs atras).
import re, math, collections, unicodedata, random
random.seed(7)

# ---------- carga Voynich con seccion ($I) y lengua ($L) ----------
SEC = {"T":"Texto","H":"Herbal","A":"Astronomico","Z":"Zodiaco",
       "B":"Biologico","C":"Cosmologico","P":"Farmaceutico","S":"Estrellas"}
def load_voynich(path):
    toks, secs = [], []
    cur_sec = None
    for raw in open(path, encoding="latin-1"):
        if raw.startswith("<") and "$I=" in raw:
            m = re.search(r"\$I=([A-Z])", raw); cur_sec = m.group(1) if m else None
        m = re.match(r"<[^>]*;H>\s*(.*)", raw)
        if not m: continue
        body = m.group(1).strip().rstrip("<->").strip()
        for w in re.split(r"[.,]", body):
            w = w.replace("!","").replace("%","")
            if not w or "?" in w or "*" in w: continue
            toks.append(w); secs.append(cur_sec)
    return toks, secs

def load_spanish(path, n):
    txt = open(path, encoding="utf-8").read()
    txt = txt.split("*** START",1)[-1].split("*** END",1)[0]
    txt = unicodedata.normalize("NFKD", txt)
    txt = "".join(c for c in txt if not unicodedata.combining(c)).lower()
    return re.findall(r"[a-z]+", txt)[:n]

def stream(toks): return " ".join(toks)

# ---------- (3) entropia condicional adelante/atras ----------
def hcond(s, n):
    def H(k):
        c = collections.Counter(s[i:i+k] for i in range(len(s)-k+1))
        t = sum(c.values()); return -sum(v/t*math.log2(v/t) for v in c.values())
    return H(n)-H(n-1) if n>1 else H(1)

# ---------- (1) informacion mutua a distancia d (nivel char) ----------
def mi_at(s, d):
    px = collections.Counter(s)
    pxy = collections.Counter((s[i], s[i+d]) for i in range(len(s)-d))
    n = len(s)-d; N = len(s)
    mi = 0.0
    for (a,b),c in pxy.items():
        pab = c/n; pa = px[a]/N; pb = px[b]/N
        mi += pab*math.log2(pab/(pa*pb))
    return mi

# ---------- (2) especificidad por seccion (KL palabra vs global) ----------
def semantic_info(toks, secs, minf=5):
    # distribucion global de tokens por seccion
    tot = collections.Counter(s for s in secs if s)
    T = sum(tot.values())
    g = {k: v/T for k,v in tot.items()}
    perword = collections.defaultdict(lambda: collections.Counter())
    freq = collections.Counter()
    for w,s in zip(toks,secs):
        if s is None: continue
        perword[w][s]+=1; freq[w]+=1
    I = 0.0; Nw = 0
    for w,cnt in perword.items():
        f = freq[w]
        if f < minf: continue
        kl = sum((c/f)*math.log2((c/f)/g[s]) for s,c in cnt.items())
        I += f*kl; Nw += f
    return I/Nw if Nw else 0.0   # bits/token de info de seccion

def semantic_null(toks, secs, minf=5, reps=20):
    lab = [s for s in secs]
    vals = []
    for _ in range(reps):
        random.shuffle(lab)
        vals.append(semantic_info(toks, lab, minf))
    m = sum(vals)/len(vals)
    sd = (sum((v-m)**2 for v in vals)/len(vals))**.5
    return m, sd

# =================== corridas ===================
voy, vsec = load_voynich("voy_lsi.txt")
esp = load_spanish("quijote_es.txt", len(voy))
sv = stream(voy); se = stream(esp)
svr = sv[::-1]; ser = se[::-1]   # invertidos

print("="*60)
print("PASO 3 — DIRECCIONALIDAD (entropia condicional, bits)")
print(f"{'':16}{'h2->':>8}{'h2<-':>8}{'h3->':>8}{'h3<-':>8}")
print(f"{'Voynich':16}{hcond(sv,2):>8.3f}{hcond(svr,2):>8.3f}{hcond(sv,3):>8.3f}{hcond(svr,3):>8.3f}")
print(f"{'Espanol':16}{hcond(se,2):>8.3f}{hcond(ser,2):>8.3f}{hcond(se,3):>8.3f}{hcond(ser,3):>8.3f}")

print("="*60)
print("PASO 1 — MEMORIA DE LARGO ALCANCE (MI a distancia d, bits)")
sh = list(sv); random.shuffle(sh); sh = "".join(sh)   # nulo: mismo char-mix
print(f"{'d':>4}{'Voynich':>10}{'Espanol':>10}{'Voy-baraj':>11}")
for d in [1,2,3,5,8,12,20,30,50,80]:
    print(f"{d:>4}{mi_at(sv,d):>10.4f}{mi_at(se,d):>10.4f}{mi_at(sh,d):>11.4f}")

print("="*60)
print("PASO 2 — ESPECIFICIDAD POR SECCION (info de seccion, bits/token)")
obs = semantic_info(voy, vsec); nul, nsd = semantic_null(voy, vsec)
print(f"Voynich observado : {obs:.4f}")
print(f"Voynich nulo(baraj): {nul:.4f} +/- {nsd:.4f}")
z = (obs-nul)/nsd if nsd else float('inf')
print(f"exceso sobre nulo : {obs-nul:+.4f} bits  (z = {z:.1f} sigmas)")
# reparto por seccion (cuantos tokens por seccion, para el paper)
cc = collections.Counter(s for s in vsec if s)
print("tokens por seccion:", {SEC.get(k,k):v for k,v in cc.most_common()})
