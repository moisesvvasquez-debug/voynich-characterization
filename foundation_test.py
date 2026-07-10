#!/usr/bin/env python3
"""
LA PRIMERA PREGUNTA: ¿podemos DEMOSTRAR que es una máquina (generador combinatorio)
y no un lexicón (lengua con vocabulario de palabras-átomo)?

Diferencia falsable = PRODUCTIVIDAD. Una máquina produce palabras NUEVAS sin parar,
predecibles desde sus partes. Un lexicón reusa un vocabulario fijo.

Test apples-to-apples (misma regla para Voynich y español):
  parte de palabra = (prefijo=primeros 2, núcleo=medio, sufijo=últimos 2), palabras len>=4.
  Split 50/50 tokens (train/test).
  Métricas en TEST:
   A) % de tokens NUEVOS (palabra no vista en train)  -> tasa de acuñación
   B) de los nuevos, % cuyas 3 partes YA se vieron en train -> "recombinación de partes conocidas"
   C) modelo factorizado P(w)=P(pre)P(core)P(suf) vs modelo lexicón: cross-entropy en test
      (cuánto mejor predice el generador las palabras nuevas) -> perplejidad
Si Voynich >> español en A y B, y su modelo factorizado sufre mucho menos con lo nuevo,
= evidencia DIRECTA de que las palabras se GENERAN de partes (máquina), no se sacan de un léxico.
"""
import re, math, collections, random
random.seed(1)

def words_voynich():
    ws=[]
    for raw in open("voy_lsi.txt",encoding="latin-1"):
        m=re.match(r"^<f[0-9]+[rv][0-9]?\.[0-9]+,[^;]*;H>\s+(.*)",raw)
        if not m: continue
        for t in re.split(r"[.,]",m.group(1).strip()):
            t=re.sub(r"[!%?*\-<>@=\s]","",t)
            if t and t.isascii() and t.isalpha(): ws.append(t)
    return ws

def words_spanish():
    txt=open("quijote_es.txt",encoding="latin-1").read().lower()
    return re.findall(r"[a-záéíóúñ]+",txt)

def parts(w):
    if len(w)<4: return None
    return (w[:2], w[2:-2] if len(w)>4 else "", w[-2:])

def analyze(name, ws):
    ws=[w for w in ws if len(w)>=4]
    random.shuffle(ws)
    half=len(ws)//2
    train, test = ws[:half], ws[half:]
    vocab=set(train)
    tp=collections.Counter(); tc=collections.Counter(); ts=collections.Counter()
    pre_seen=set(); core_seen=set(); suf_seen=set()
    for w in train:
        p=parts(w)
        if not p: continue
        tp[p[0]]+=1; tc[p[1]]+=1; ts[p[2]]+=1
        pre_seen.add(p[0]); core_seen.add(p[1]); suf_seen.add(p[2])
    Np=sum(tp.values()) or 1; Nc=sum(tc.values()) or 1; Ns=sum(ts.values()) or 1

    novel=0; novel_parts_known=0; ntest=0
    # cross-entropy
    wc=collections.Counter(train); Wt=sum(wc.values())
    ce_lex=0.0; ce_fac=0.0; V=len(vocab)
    for w in test:
        p=parts(w)
        if not p: continue
        ntest+=1
        is_novel = w not in vocab
        if is_novel:
            novel+=1
            if p[0] in pre_seen and p[1] in core_seen and p[2] in suf_seen: novel_parts_known+=1
        # lexicón: add-1 sobre vocab+UNK
        p_lex=(wc.get(w,0)+1)/(Wt+V+1)
        ce_lex+= -math.log2(p_lex)
        # factorizado: producto de marginales (add-1)
        pp=(tp.get(p[0],0)+1)/(Np+len(pre_seen)+1)
        pcc=(tc.get(p[1],0)+1)/(Nc+len(core_seen)+1)
        pss=(ts.get(p[2],0)+1)/(Ns+len(suf_seen)+1)
        ce_fac+= -math.log2(pp*pcc*pss)
    ce_lex/=ntest; ce_fac/=ntest
    print(f"\n=== {name}  ({len(ws):,} palabras len>=4) ===")
    print(f"A) tokens NUEVOS en test (no vistos en train): {100*novel/ntest:.1f}%")
    print(f"B) de los nuevos, % con las 3 PARTES ya vistas: {100*novel_parts_known/novel:.1f}%  "
          f"(= {100*novel_parts_known/ntest:.1f}% del test = palabras nuevas recombinadas de partes conocidas)")
    print(f"C) cross-entropy en test:  lexicón={ce_lex:.2f} bits/palabra   factorizado(partes)={ce_fac:.2f}")
    print(f"   -> el generador de partes {'GANA' if ce_fac<ce_lex else 'pierde'} por {ce_lex-ce_fac:+.2f} bits "
          f"(negativo = el lexicón predice mejor = más parecido a lengua)")
    return dict(novel=novel/ntest, recomb=novel_parts_known/ntest, ce_lex=ce_lex, ce_fac=ce_fac)

V=analyze("VOYNICH (herbal)", words_voynich())
E=analyze("ESPAÑOL (Quijote)", words_spanish())
print("\n=== VEREDICTO ===")
print(f"acuñación de palabras nuevas:  Voynich {100*V['novel']:.0f}%  vs  español {100*E['novel']:.0f}%")
print(f"nuevas-recombinadas-de-partes: Voynich {100*V['recomb']:.0f}%  vs  español {100*E['recomb']:.0f}%")
print(f"ventaja del generador sobre lexicón: Voynich {V['ce_lex']-V['ce_fac']:+.2f}  vs  español {E['ce_lex']-E['ce_fac']:+.2f} bits")
print("Si Voynich supera claramente al español en las tres -> las palabras se GENERAN de partes = MÁQUINA (demostrado por productividad).")
