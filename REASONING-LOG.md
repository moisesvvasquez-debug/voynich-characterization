# Voynich — Log de razonamiento (el PATRÓN de resolución)

*Sesión 2026-07-07. Documenta cómo llegamos al resultado — porque el método es reutilizable (es el motor de resolución de problemas aplicado al caso más difícil que existe).*

---

## El meta-método (el patrón, extraíble a cualquier problema)

1. **No resolver antes de probar que hay algo que resolver.** Antes de "descifrar", preguntar: ¿esto carga información o es ruido? (Decidible sin leer.)
2. **Medir contra baselines honestos.** Todo hallazgo se compara contra: lengua real (español), ruido puro (orden-0), y la propia data barajada. Sin baseline, un número no dice nada.
3. **Reportar los NO como resultados.** Cada hipótesis muerta acota el espacio. Los cribs fallidos valen tanto como los positivos.
4. **Dejar que dos medidas independientes converjan.** No forzar una lectura; buscar cuándo dos análisis separados apuntan al mismo mecanismo (ahí está la señal real).
5. **Invertir supuestos mentales.** Dirección de lectura, "el dibujo ilustra el texto", "es prosa lineal" — testear cada supuesto, no asumirlo.
6. **Buscar el precedente histórico/físico.** Un mecanismo abstracto gana peso si existió de verdad (Llull, Alberti, Friedman).
7. **Parar en el límite honesto.** Reconocer cuándo la evidencia disponible ya no puede decidir, en vez de sobre-afirmar.

---

## La cadena concreta (hipótesis → test → resultado)

| # | Pregunta / hipótesis | Test | Resultado |
|---|---|---|---|
| 1 | ¿Hay mensaje o es ruido? | Zipf, TTR, entropía vs baselines | **Hay mensaje** (rechazado ruido) |
| 2 | ¿Por qué es raro? | entropía condicional h2 | h2=2.26 << 3.04 español (anomalía famosa, reproducida) |
| 3 | ¿Carga significado? | KL por sección vs nulo | **165σ** — vocabulario sigue el tema (sobrevive control A/B, 75-77σ) |
| 4 | ¿Es lengua fonética? | gramática de palabra (ranuras) | NO — prefijo/sufijo casi obligatorios → no alfabeto llano |
| 5 | (idea usuario) ¿canto/tono/énfasis? | LAAFU, largo de línea, strip 1er glifo | tono NO, canto NO (CV 0.45), **énfasis SÍ** (glifo añadido daiin→aiin) |
| 6 | Cribs del zodiaco (Turing) | etiquetas: ¿números?/¿nombres? | ambos MUERTOS (267/296 únicas; co-ref 1.1×) |
| 7 | ¿Qué distingue secciones? | keywords por sección | morfología (afijos), no lexemas de contenido |
| 8 | ¿Es prosa lineal? | MI dentro vs entre líneas | NO — línea = unidad cerrada (1.72 vs 0.29) |
| 9 | (idea usuario) ¿proceso/receta? | repetición de trigramas | NO — anti-repetitivo (0.2% vs 9.6% español) |
| 10 | (idea usuario) mapear layout | tipo+posición de bloques vs imagen | **gramática espacial**: layout→contenido 100% en páginas con figura |
| 11 | ¿Las palabras son código combinatorio? | descomposición pre+núcleo+suf | SÍ — 62% vs 18% español; 15 pre × 17 suf; dial chico |
| 12 | (idea usuario) orden = significado | MI(posición;prefijo) | SÍ, 6.6× nulo |
| 13 | (idea usuario) 324 días / secuencia | gradiente en recetas | NO — homogéneo (r=+0.04); 360 zodiaco es el nº limpio |
| 14 | ¿Qué mecanismo histórico? | literatura | **rueda de Llull** → (cripto) Alberti→Enigma; (lengua) a priori→**Friedman** |
| 15 | ¿Rueda con significado o mecánica? | acoplamiento pre×suf; auto-citación | acoplado (gramática, 24×); pero auto-similitud ≈ español → **NO decidible por texto** |
| — | Visual | f69r escaneo | **es una rota/rueda literal** (anillos+radios+rosetón) |

---

## Terminus honesto

Las dos hipótesis vivas — **rueda-con-significado** (lengua a priori, Friedman) vs **rueda-mecánica-vacía** (auto-cita, Timm-Schinner/Rugg) — **comparten firma estadística de superficie** porque un código de dial chico produce los mismos vecinos casi-idénticos que una copia mecánica. El texto solo no las separa. El único fiel de la balanza es la semántica global (165σ), que inclina débilmente a **significado**. El desempate definitivo requiere el enlace **figura→código** (visión a escala), pendiente.

**No desciframos el Voynich. Caracterizamos su maquinaria y nombramos su mecanismo — y delimitamos con precisión qué falta para cerrarlo.**
