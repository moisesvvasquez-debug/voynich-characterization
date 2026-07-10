# Exploración KTD por motor de ideas — resultados (2026-07-10)

Método: motor de ideas (`idea_engine.py`, 3984 ideas generadas por inversión de supuestos,
rankeadas por prior KTD → `IDEAS-VOYNICH-ENGINE.md`). Movidas top: CRUZAR, GENERAR, CRIB-ESTRUCTURAL.
Luego se corrieron los tests decisivos, deteniéndose al hallar algo que sobrevive KTD.

## Tests corridos y veredictos

| # | Idea (por inversión) | Test | Veredicto KTD |
|---|---|---|---|
| 1 | ¿Es latín con abreviación medieval? (INV A5) | `abbrev_latin_test.py` | ❌ **MUERE** — abreviar sube h₂ (3.5→3.55) y baja templateado (16%→9%); no reproduce el perfil (2.12 / 68%) |
| 2 | ¿El residuo 19% es el contenido? (INV A8) | `residual_test.py` | ❌ **MUERE** — conformes y no-conformes cargan la MISMA señal de tema (KL neta 0.370 vs 0.372) |
| 3 | ¿Compresión distingue sentido vs generador? | `ktd_explore.py` T1 | ⚪ **CONFIRMA** — Voynich (0.275) ≈ su i.i.d. (0.277) ≈ barajado (0.283); sin estructura extra al unigrama |
| 4 | ¿Memoria secuencial de palabra? (unigrama vs bigrama) | `ktd_explore.py` T2 | ⚪ **CONFIRMA** — mejora del bigrama −0.84 bits (menos orden que una lengua real) |
| 5 | **¿Regla de enganche entre palabras?** (suf_i → pre_{i+1}) | inline | ✅ **SOBREVIVE** — ver abajo |

## ✅ Hallazgo que sobrevive: regla de enganche inter-palabra

**MI(sufijo de palabra_i ; prefijo de palabra_{i+1}) = 0.111 bits.**
- vs nulo global (sin sección): exceso +0.100.
- vs nulo **dentro de sección** (aísla el confundido temático): exceso **+0.096, z=+110** → NO es la sección.
- excluyendo **casi-copias** (edit≤1, 5% de pares; controla auto-copia Timm-Schinner): MI=0.111, exceso **+0.096, z=+88** → NO es auto-copia.
- El sufijo es ~neutral a la posición → **no es** confundido de posición.
- Comparación: prefijo_i→prefijo_{i+1} también significativo (0.056, z=+60); acoplamiento interno pre;suf = 0.225.

**Interpretación (honesta):** el Voynich tiene **estructura secuencial real a nivel de palabra** — es
**al menos Markov-1 en los afijos**: cómo termina una palabra condiciona cómo empieza la siguiente.

**Corrige un overclaim del paper:** "una máquina mínima i.i.d. de palabras reproduce TODO" es demasiado
fuerte — un i.i.d. NO produce este enganche. La máquina mínima reproduce carácter/unigrama, pero **no**
la dependencia inter-palabra. El sistema es **más estructurado que i.i.d.**

**Lo que NO prueba:** un generador Markov también tiene esto → **no decide** significado-vs-mecanismo.
Es un mecanismo más estructurado, no evidencia de sentido.

## Pendiente
- Sumar al paper: (a) los dos negativos (abreviación, residuo) como hipótesis descartadas;
  (b) el hallazgo del enganche inter-palabra + la corrección del claim i.i.d.
- Luego cortar Release v1.1.0 → actualiza DOI.
Scripts: `idea_engine.py`, `abbrev_latin_test.py`, `residual_test.py`, `ktd_explore.py`.
