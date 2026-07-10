# Test de ETIQUETAS (crib con referente tight) — resultado 2026-07-08

## Qué es
El límite exacto que faltaba: un párrafo está junto a TODA una planta (referente difuso),
pero una ETIQUETA está pegada a UN objeto dibujado. Test: ¿el ajuste del dial de una etiqueta
(prefijo/sufijo) predice el TIPO de parte que rotula? Sección farmacéutica = partes sueltas
(raíces/hojas/flores en tarros de botica), el referente más tight del manuscrito.

## Cómo (harness: label_extract.py + label_crib.py)
1. Extracción: 968 etiquetas en 51 folios (loci tipo @L;H). SON combinatorias (85% se descomponen,
   igual que los párrafos 83%) → las etiquetas son la misma máquina.
2. Visión (Claude Sonnet-5): anotó los objetos rotulados por folio farmacéutico.
   GOTCHA CLAVE resuelto: scan≠2·folio-1 tras los foldouts. f99r=scan175 (no 197), verificado por
   nº de esquina. Override en SCAN_OVERRIDE (f99r-f102v=175-182).
3. Compuerta de alineación: visión ve conteos correctos (f100r 18=18, f99r 34≈35) = scans correctos.
4. Cruce afijo↔part_type + permutación (1000) + out-of-sample (split folios).

## Resultado: NULO
- 78 etiquetas emparejadas (f99r,f99v,f100r,f101v). Baseline: root 31%, whole_plant 29%, jar 13%...
- PREFIJO: señales fuertes REAL=0 (nulo hasta 3). SUFIJO: REAL=0 (nulo hasta 5).
- Out-of-sample: prefijo acc 0.12, sufijo 0.28 — POR DEBAJO del naive 0.31.
- El ajuste de etiqueta NO predice el tipo de parte. El referente más tight también da nulo.

## Interpretación (honesta)
Tercer nulo figura→código independiente (herbal 7B, herbal Claude, ahora etiquetas). El texto no
mapea la morfología visible en NINGÚN nivel probado. Inclina hacia: (a) generador mecánico sin
referente, o (b) código cuyo referente NO es la forma del dibujo (¿esencia/virtud/nombre, no forma?).

## Caveats (por qué es piloto fuerte, no veredicto final)
- n=78 modesto; emparejamiento por orden de lectura con ±1-2 de desfase → DILUYE señal real
  (pero el OOS por DEBAJO del naive, no solo en azar, refuerza el nulo).
- Taxonomía de visión gruesa (raíz/hoja/flor); la etiqueta podría cifrar algo más fino.
- Rigor total = recorte espacial por etiqueta (cuál etiqueta junto a cuál objeto) + taxonomía fina.

Archivos: label_extract.py, label_crib.py, labels.json, label_objects.json, label_crib2.log

## v2 RIGUROSO (2026-07-08) — confirma y fortalece el nulo
Mejoras: forzar N exacto a la visión + pedir coordenadas + emparejar por orden de lectura 2D
(fila→columna) + agregar sub-paneles de foldout + cruzar part y part+color.
- Visión devolvió N exacto en 6/7 folios -> 103 etiquetas pareadas (vs 78 del piloto), 6 folios.
- part: prefijo 0, sufijo 1 (nulo hasta 4) = NULO. OOS 0.12 vs naive 0.34.
- part+color: prefijo 0, sufijo 0 = NULO. OOS 0.06 vs naive 0.20.
- CLAVE: OOS MUY por debajo del naive en ambos -> el mapa afijo->parte aprendido en media muestra
  MIS-predice la otra media = ruido puro, sin señal diluida escondida.
- Caveat restante (menor): coords de visión no son ground-truth absoluto; un código que cifre
  IDENTIDAD/nombre/virtud (no forma visible) no lo cazaría (límite de lo testeable por imagen).
Harness: label_crib_v2.py, label_objects_v2.json, label_v2.log.
CONCLUSIÓN FIRME: no hay mapeo texto->morfología-visible en NINGÚN nivel (herbal ×2 + etiquetas rig).
