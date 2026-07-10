#!/usr/bin/env python3
# Metricas comparativas Aramaico/Siriaco (Peshitta) vs Voynich.
# Replica la metodologia de battery.py: char stream = " ".join(tokens),
# h2 = blockH(2)-blockH(1). Controles: arabe (Coran) y espanol (Quijote).
import re, math, collections, unicodedata, sys

# ---------- metricas comunes ----------
def char_stream(tokens):
    return " ".join(tokens)

def blockH(stream, k):
    c = collections.Counter(stream[i:i+k] for i in range(len(stream)-k+1))
    tot = sum(c.values())
    return -sum(v/tot*math.log2(v/tot) for v in c.values())

def h2_cond(tokens):
    s = char_stream(tokens)
    return blockH(s, 2) - blockH(s, 1)

def wordlen_mean(tokens):
    L = [len(w) for w in tokens]
    return sum(L)/len(L)

def top10_load(tokens):
    c = collections.Counter(tokens)
    top = sum(f for _, f in c.most_common(10))
    return 100.0*top/len(tokens)

def trigram_rep(tokens):
    # % de las ocurrencias de 3-gramas (de palabras) que pertenecen a
    # trigramas que aparecen >1 vez (ponderado por ocurrencias)
    tri = collections.Counter(tuple(tokens[i:i+3]) for i in range(len(tokens)-2))
    total = sum(tri.values())
    repeated = sum(v for v in tri.values() if v > 1)
    return 100.0*repeated/total

def vowel_fraction(tokens, vowel_set):
    letters = [ch for w in tokens for ch in w]
    if not letters: return 0.0
    v = sum(1 for ch in letters if ch in vowel_set)
    return 100.0*v/len(letters)

# ---------- cargadores ----------
def strip_combining(txt):
    return "".join(c for c in txt if not unicodedata.combining(c))

def load_syriac(path):
    txt = open(path, encoding="utf-8").read()
    txt = strip_combining(unicodedata.normalize("NFD", txt))
    # letras siriacas U+0710..U+072F (base). Tokenizar en runs de esas letras.
    toks = re.findall(r"[ܐ-ܯ]+", txt)
    return toks

def load_arabic(path, max_tokens=200000):
    txt = open(path, encoding="utf-8").read()
    txt = strip_combining(unicodedata.normalize("NFD", txt))  # quita harakat
    toks = re.findall(r"[ء-ي]+", txt)
    return toks[:max_tokens]

def load_spanish(path, max_tokens=200000):
    txt = open(path, encoding="utf-8").read()
    txt = unicodedata.normalize("NFKD", txt)
    txt = "".join(c for c in txt if not unicodedata.combining(c)).lower()
    toks = re.findall(r"[a-z]+", txt)
    return toks[:max_tokens]

# vocales / matres lectionis
SYR_VOWELS = {"ܐ", "ܘ", "ܝ"}  # alaph, waw, yod
# arabe: alif, waw, ya, (+ alif variants, ta marbuta no)
AR_VOWELS = {"ا", "و", "ي", "آ", "أ", "إ", "ى"}
ES_VOWELS = set("aeiou")

def report(name, tokens, vowel_set):
    print(f"\n=== {name} ===")
    print(f"  word count       : {len(tokens):,}")
    print(f"  mean word length : {wordlen_mean(tokens):.2f}")
    print(f"  top-10 load      : {top10_load(tokens):.1f}%")
    print(f"  trigram-rep      : {trigram_rep(tokens):.2f}%")
    print(f"  h2 (cond entropy): {h2_cond(tokens):.2f} bits")
    print(f"  vowel fraction   : {vowel_fraction(tokens, vowel_set):.1f}%")
    # top-10 palabras
    c = collections.Counter(tokens)
    print("  top-10 words     :", " ".join(w for w,_ in c.most_common(10)))
    return tokens

if __name__ == "__main__":
    base = "/Users/moisesvasquez/voynich-poc/"
    syr = load_syriac(base+"aramaic_peshitta_raw.txt")
    report("SYRIAC / ARAMAIC (Peshitta OT, unvocalized)", syr, SYR_VOWELS)

    try:
        ar = load_arabic(base+"quran_raw.txt")
        report("ARABIC control (Quran)", ar, AR_VOWELS)
    except Exception as e:
        print("arabic control skipped:", e)

    try:
        es = load_spanish(base+"quijote_es.txt")
        report("SPANISH control (Quijote)", es, ES_VOWELS)
    except Exception as e:
        print("spanish control skipped:", e)

    print("\n=== VOYNICH reference (given) ===")
    print("  word length 5.4, top-10 11%, trigram-rep 0.7%, h2 2.24, vowels 46%")
