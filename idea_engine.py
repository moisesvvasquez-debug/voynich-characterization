# -*- coding: utf-8 -*-
# MOTOR DE IDEAS (Voynich) — reproduce nuestro sistema: genera el espacio de ideas
# combinando {supuesto} x {operador} x {objetivo} x {canal}, y puntúa cada una con
# priors KTD. Los scores son PRIORS (no medidos): sirven para PRIORIZAR, no decidir.
import itertools, re

# ---------- dimensiones ----------
ASSUMP = {  # supuestos/conclusiones a desafiar (clave -> frase)
 "A1":"el texto carga información (no es galimatías)",
 "A2":"la estructura es combinatoria (ranuras, no léxico)",
 "A3":"significado-vs-mecanismo es indecidible desde el texto",
 "A4":"las imágenes no codifican el texto (figura→código nulo)",
 "A5":"ninguna lengua natural encaja (entropía muy baja)",
 "A6":"la unidad reutilizada es sub-palabra",
 "A7":"el orden dentro del texto no cuenta",
 "A8":"el residuo/excepciones son ruido",
 "A9":"los cribs fónicos multilingüe son azar",
 "A10":"es un solo sistema (ajustes A/B de Currier)",
 "A11":"la señal de sección vive en los afijos",
 "A12":"es de tipo lista/inventario (no prosa)",
 "A13":"el dial de grado/cualidad es ordinal",
 "A14":"las plantas son quiméricas/decorativas",
 "A15":"la -m es una floritura terminal",
 "A16":"un generador mínimo (i.i.d. de palabras) reproduce todo",
}
OPS = {  # operadores de investigación
 "INVERTIR":("asumir lo contrario de", 0.0),
 "RE-ESCALA-ARRIBA":("mirar a nivel línea/página/libro", 0.15),
 "RE-ESCALA-ABAJO":("mirar a nivel glifo/trazo", 0.10),
 "RE-CANAL-IMAGEN":("usar los escaneos del Beinecke para", -0.25),
 "RE-CANAL-LAYOUT":("usar la metadata de posición/layout para", 0.10),
 "RE-CANAL-CODICOLOGIA":("usar tinta/correcciones/cuadernillos para", -0.35),
 "RESIDUALIZAR":("estudiar las excepciones de", 0.05),
 "CONDICIONAR-SECCION":("separar por sección y re-testear", 0.05),
 "CONDICIONAR-ESCRIBA":("separar por mano/Currier A-B y re-testear", 0.05),
 "CONDICIONAR-POSICION":("separar por posición en la línea", 0.05),
 "COMPARAR-CORPUS":("comparar contra un corpus de referencia nuevo (braquigrafía/lengua construida/cifra/glosolalia/tablas)", 0.10),
 "DESCOMPONER":("descomponer en unidades más finas", 0.05),
 "AGREGAR":("agregar en unidades más gruesas", 0.05),
 "REORDENAR":("test de permutación/secuencia sobre", 0.05),
 "CRUZAR":("cruzar dos señales (texto×imagen, deriva×sección)", 0.15),
 "GENERAR":("construir un modelo generativo y comparar por verosimilitud/AIC", 0.20),
 "CRIB-ESTRUCTURAL":("un crib estructural (no fónico) sobre", 0.10),
}
TARGETS = {  # qué se mide
 "entropía":0.5,"estructura-de-palabra":0.5,"señal-de-sección":0.7,"enlace figura-código":0.25,
 "orden/secuencia":0.4,"deriva por folio":0.5,"etiquetas":0.5,"gallows/glifos-clave":0.4,
 "dial de grado":0.45,"palabras-función":0.55,"hapax/rareza":0.4,"formato de línea":0.45,
 "compresión/complejidad":0.5,"co-ocurrencia/red":0.55,"patrones de error":0.5,
}
CH = {  # canal -> (frase, testeable_ahora 0..1)
 "texto":("(transliteración)",0.90),"imagen":("(escaneos)",0.55),"layout":("(metadata de posición)",0.82),
 "codicología":("(rasgos físicos)",0.32),"corpus-externo":("(otra data de comparación)",0.72),
}
# operadores atados a un canal (para coherencia)
OP_CH = {"RE-CANAL-IMAGEN":"imagen","RE-CANAL-LAYOUT":"layout","RE-CANAL-CODICOLOGIA":"codicología",
         "COMPARAR-CORPUS":"corpus-externo","CRIB-ESTRUCTURAL":"corpus-externo"}

# ---------- ya MUERTAS (novedad ~0) ----------
DEAD = [("figura-código","texto-nivel-palabra"),("cribs fónicos",),("lengua natural",),
        ("números",),("abreviación",),("residuo-contenido",)]
DEAD_KEYS = {("A4","enlace figura-código"),("A9",),("A5","COMPARAR-CORPUS"),}  # heurística

def testable(op,ch):
    base=CH[ch][1]; return max(0.05,min(1.0, base+OPS[op][1]))
def novelty(a,op,tgt):
    n=0.62
    if a=="A4" and tgt=="enlace figura-código" and op not in ("CRUZAR","RE-CANAL-IMAGEN"): n=0.15
    if a=="A9": n=0.20
    if a=="A5" and op=="COMPARAR-CORPUS" and tgt=="entropía": n=0.18   # abreviación ya corrida
    if a=="A8" and op=="RESIDUALIZAR": n=0.15                          # residuo ya corrido
    if a=="A15": n=0.25
    if op in ("GENERAR","CRUZAR","CRIB-ESTRUCTURAL","RE-CANAL-CODICOLOGIA"): n+=0.12
    return max(0.05,min(1.0,n))
def decisive(op,tgt):  # ¿podría inclinar meaning-vs-mechanism?
    d=0.25
    if op in ("GENERAR","CRUZAR","CRIB-ESTRUCTURAL","RE-CANAL-CODICOLOGIA","RE-CANAL-IMAGEN"): d+=0.35
    if tgt in ("enlace figura-código","compresión/complejidad","patrones de error"): d+=0.20
    return min(1.0,d)

def coherent(a,op,tgt,ch):
    # el canal debe casar con el operador si el operador fija canal
    if op in OP_CH and ch!=OP_CH[op]: return False
    if op not in OP_CH and ch in ("imagen","codicología"): return False  # esos canales solo por RE-CANAL-*
    # algunos objetivos no aplican a algunos operadores (poda mínima)
    if op=="RE-CANAL-CODICOLOGIA" and tgt in ("entropía","co-ocurrencia/red","palabras-función"): return False
    if op=="RE-CANAL-IMAGEN" and tgt in ("entropía","formato de línea","palabras-función"): return False
    return True

ideas=[]
for a,op,tgt in itertools.product(ASSUMP,OPS,TARGETS):
    ch = OP_CH.get(op, "texto" if tgt not in ("etiquetas",) else "texto")
    if not coherent(a,op,tgt,ch): continue
    t=testable(op,ch); n=novelty(a,op,tgt); d=decisive(op,tgt); s=TARGETS[tgt]
    score = 0.34*t + 0.24*n + 0.24*s + 0.18*d      # prior KTD
    txt=f"{OPS[op][0]} «{ASSUMP[a]}» — sobre {tgt} {CH[ch][0]}"
    ideas.append((round(score,3),a,op,tgt,ch,txt,round(t,2),round(n,2),round(d,2),round(s,2)))

# dedupe por texto
seen=set(); uniq=[]
for it in ideas:
    if it[5] in seen: continue
    seen.add(it[5]); uniq.append(it)
uniq.sort(reverse=True)

print(f"IDEAS GENERADAS (coherentes, únicas): {len(uniq)}")
print(f"(espacio bruto: {len(ASSUMP)}×{len(OPS)}×{len(TARGETS)} = {len(ASSUMP)*len(OPS)*len(TARGETS)})\n")

# --- MOVIDAS: score medio por operador (qué TIPO de test rinde más) ---
from collections import defaultdict
opsum=defaultdict(list)
for it in uniq: opsum[it[2]].append(it[0])
print("MOVIDAS rankeadas (score-prior medio del operador):")
for op,ss in sorted(opsum.items(), key=lambda kv:-sum(kv[1])/len(kv[1]))[:8]:
    print(f"   {sum(ss)/len(ss):.3f}  {op}")

# --- TOP DIVERSO: mejor idea por (operador,objetivo), sin repetir la misma movida ---
best={}
for it in uniq:
    key=(it[2],it[3])
    if key not in best: best[key]=it
diverse=sorted(best.values(), reverse=True)
print("\nTOP 20 DIVERSO (una por movida×objetivo)  [T=testeable N=novedad D=decisivo Sig=señal]")
print("-"*100)
for it in diverse[:20]:
    print(f"{it[0]:.3f} [{it[2]:<20}| {it[3]:<20}] T{it[6]} N{it[7]} D{it[8]}  {it[5][:60]}")

# guardar todo
with open("IDEAS-VOYNICH-ENGINE.md","w",encoding="utf-8") as fh:
    fh.write(f"# Motor de ideas Voynich — {len(uniq)} ideas rankeadas (score-prior KTD)\n\n")
    fh.write("> Los scores son PRIORS (no medidos): priorizan, no deciden. La decisión se toma corriendo el test.\n\n")
    fh.write("| # | score | supuesto | operador | objetivo | canal | T | N | D | Sig | idea |\n|--|--|--|--|--|--|--|--|--|--|--|\n")
    for i,it in enumerate(uniq,1):
        fh.write(f"| {i} | {it[0]:.3f} | {it[1]} | {it[2]} | {it[3]} | {it[4]} | {it[6]} | {it[7]} | {it[8]} | {it[9]} | {it[5]} |\n")
print(f"\nGuardado: IDEAS-VOYNICH-ENGINE.md ({len(uniq)} ideas)")
