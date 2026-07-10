#!/usr/bin/env python3
# Bateria de autenticidad Voynich: senal vs ruido.
# Compara Voynich (Takahashi) contra espanol (Quijote), Voynich barajado,
# y aleatorio orden-0. Metricas: entropias h1/h2/h3, Zipf, long. de palabra.
import re, math, collections, unicodedata, random

random.seed(42)

# ---------- carga Voynich (solo lineas Takahashi ;H>) ----------
def load_voynich(path):
    toks_all, toks_by_lang = [], {"A": [], "B": []}
    cur_lang = None
    for raw in open(path, encoding="latin-1"):
        # cabecera de pagina: <f1r> ... $L=A ...
        if raw.startswith("<") and "$L=" in raw:
            m = re.search(r"\$L=([AB])", raw)
            cur_lang = m.group(1) if m else None
        # linea de datos Takahashi
        m = re.match(r"<[^>]*;H>\s*(.*)", raw)
        if not m:
            continue
        body = m.group(1).strip()
        body = body.rstrip("<->").strip()          # quita marcas de fin
        for w in re.split(r"[.,]", body):           # . , = separador de palabra
            w = w.replace("!", "").replace("%", "") # ! = relleno alineacion
            if not w:
                continue
            if "?" in w or "*" in w:                # palabra con glifo ilegible
                continue
            toks_all.append(w)
            if cur_lang in toks_by_lang:
                toks_by_lang[cur_lang].append(w)
    return toks_all, toks_by_lang

# ---------- carga espanol (letras + espacio, sin tildes) ----------
def load_spanish(path, max_tokens=40000):
    txt = open(path, encoding="utf-8").read()
    # recorta cabecera/pie Gutenberg
    txt = txt.split("*** START", 1)[-1].split("*** END", 1)[0]
    txt = unicodedata.normalize("NFKD", txt)
    txt = "".join(c for c in txt if not unicodedata.combining(c))
    txt = txt.lower()
    toks = re.findall(r"[a-z]+", txt)
    return toks[:max_tokens]

# ---------- metricas ----------
def char_stream(tokens):
    # une palabras con un espacio -> flujo de caracteres estilo literatura
    return " ".join(tokens)

def entropy_order(stream, n):
    # H(X_n | X_1..X_{n-1}) = H(ngram_n) - H(ngram_{n-1})
    def blockH(k):
        c = collections.Counter(stream[i:i+k] for i in range(len(stream)-k+1))
        tot = sum(c.values())
        return -sum(v/tot*math.log2(v/tot) for v in c.values())
    if n == 1:
        return blockH(1)
    return blockH(n) - blockH(n-1)

def zipf_slope(tokens):
    freq = sorted(collections.Counter(tokens).values(), reverse=True)
    xs = [math.log(i+1) for i in range(len(freq))]
    ys = [math.log(f) for f in freq]
    n = len(xs); sx=sum(xs); sy=sum(ys)
    sxx=sum(x*x for x in xs); sxy=sum(x*y for x,y in zip(xs,ys))
    slope = (n*sxy - sx*sy)/(n*sxx - sx*sx)
    return slope

def wordlen_stats(tokens):
    L = [len(w) for w in tokens]
    mean = sum(L)/len(L)
    var = sum((x-mean)**2 for x in L)/len(L)
    return mean, math.sqrt(var)

def report(name, tokens):
    s = char_stream(tokens)
    h1 = entropy_order(s, 1)
    h2 = entropy_order(s, 2)
    h3 = entropy_order(s, 3)
    alpha = len(set(s.replace(" ", "")))
    ttr = len(set(tokens))/len(tokens)
    zl = zipf_slope(tokens)
    wm, wsd = wordlen_stats(tokens)
    print(f"{name:22} {len(tokens):>7,} {len(set(tokens)):>6,} {ttr:>5.3f} "
          f"{alpha:>4} {h1:>5.2f} {h2:>5.2f} {h3:>5.2f} {zl:>6.2f} "
          f"{wm:>5.2f} {wsd:>5.2f}")
    return dict(h1=h1, h2=h2, h3=h3)

# ---------- corridas ----------
voy_all, voy_lang = load_voynich("voy_lsi.txt")
esp = load_spanish("quijote_es.txt", max_tokens=len(voy_all))

# barajado: mismas palabras, orden destruido (mata correlacion larga)
voy_shuf = voy_all[:]; random.shuffle(voy_shuf)
# aleatorio orden-0: mismas frecuencias de char, sin estructura de palabra
chars = list(char_stream(voy_all).replace(" ", ""))
random.shuffle(chars)
# reparte en palabras de longitud tomada de la distribucion real
lens = [len(w) for w in voy_all]; random.shuffle(lens)
rnd_toks, i = [], 0
for L in lens:
    if i+L > len(chars): break
    rnd_toks.append("".join(chars[i:i+L])); i += L

print("corpus                  tokens  tipos   TTR  alf   h1   h2   h3   zipf  wlen  wsd")
print("-"*88)
report("Voynich (todo)",      voy_all)
report("  Voynich lengua A",  voy_lang["A"])
report("  Voynich lengua B",  voy_lang["B"])
report("Espanol (Quijote)",   esp)
report("Voynich BARAJADO",    voy_shuf)
report("Aleatorio orden-0",   rnd_toks)
print("-"*88)
print("h1=entropia por char | h2=condicional (dado 1 previo) | h3=(dado 2 previos)")
print("wlen=largo medio de palabra | wsd=desviacion | zipf=pendiente (~ -1 en lengua natural)")
