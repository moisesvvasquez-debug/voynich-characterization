# Protocolo de anotación imagen→código (turnkey para vision-LLM)

Objetivo: **verificar (o refutar) el puente figura↔texto** — ¿el tipo de parte de planta dibujada correlaciona con la parte de palabra de su etiqueta? Diseñado para que un pipeline de visión lo corra sin intervención humana (sin sesgo).

## Hipótesis
Palabra Voynich = prefijo + núcleo + sufijo. Planta = raíz + hoja + flor. **Si los inventarios se corresponden**, un tipo de parte-de-planta debería predecir una parte-de-palabra (p.ej. raíz↔prefijo `ok-`). Sub-pregunta (idea del usuario): si una palabra NO correlaciona con ninguna parte visible sino que aparece en plantas visualmente distintas → nombra una **propiedad abstracta** (virtud/esencia/alma vegetal), no una cosa física.

## Datos de entrada
Escaneos: `archive.org/download/voynich/NNN.jpg` (full-res). **REQUISITO: obtener el índice folio↔scan exacto** de voynich.nu (la estimación scan≈1.76×folio se corre ~1 folio y NO sirve para folios específicos).

Dos frentes:
### Frente A — partes farmacéuticas ROTULADAS (más limpio, ~150 partes)
- Folios f88–f102. Cada parte de planta dibujada tiene su etiqueta (locus tipo `L*` en la transliteración).
- Etiquetas ya extraídas: f99r=34, f99v=25, f100r=17 (en memoria/scripts). Están en orden de lectura → alinear con las partes de izq→der.

### Frente B — plantas herbales con palabra DISCRIMINANTE
- Palabras que aparecen en solo 4–6 folios herbales (discriminan). Ejemplos ya calculados:
  - `pchor` → f2v, f9v, f19r, f21r, f45r, f52v
  - `otcho` → f1v, f14r, f15r, f32r, f47r, f96r
  - `sheky` → f2r, f29r, f29v, f39v, f46r, f95r1
  - `cham`, `qokchey`, `qokody` … (170 discriminantes en total)
- NO usar `daiin` (en 115/128 folios) ni `chol` (86) — ubicuas, no discriminan.

## Esquema de anotación (prompt fijo por figura, criterio CONSTANTE)
Para cada parte/planta, el vision-LLM devuelve JSON:
```
{ "part_type": "root|leaf|flower|tendril|pod|tube|bulb|other",
  "root_form": "taproot|branching|bulbous|fibrous|na",
  "leaf_form": "pinnate|simple|lobed|serrated|na",
  "color": ["green","brown","red","blue"],
  "n_leaflets": <int|null> }
```
Mismo prompt para las ~150 partes → etiquetas reproducibles, sin criterio variable.

## Cruce (estadística, no ojo)
1. Para cada etiqueta, descomponer en (prefijo, núcleo, sufijo) con los inventarios PRE/SUF ya definidos (`comtrade`… no: ver `battery.py`/`cribs.py`).
2. Tabla de contingencia **part_type × prefijo** (y × sufijo).
3. **χ² / información mutua** part_type↔prefijo vs. un nulo permutado.
4. Frente B: para cada palabra discriminante, ¿sus 4–6 plantas comparten un `part_type`/`root_form` más que plantas al azar? (test exacto, no impresión).

## Criterio de éxito (anti-trampa del 97%)
- NO vale una correspondencia suelta. Vale una **regla sistemática**: el mismo prefijo→mismo tipo de parte **en todas** las apariciones, verificada out-of-sample (aprender en mitad de las partes, predecir la otra mitad).
- Reportar el χ² y el acierto out-of-sample. Si predice > azar de forma estable → **primer puente figura→código verificado.**
- Si NO correlaciona con ninguna parte física pero sí es consistente por planta → candidato a **propiedad/esencia** (responde la pregunta cosa-vs-virtud).

## Herramienta
Cualquier vision-LLM con API (Qwen-VL, etc.) corriendo el prompt fijo sobre cada crop. Los crops se sacan con `sips -c H W --cropOffset Y X` (probado) una vez que se tiene el índice folio↔scan + las coordenadas de cada figura (de la transliteración o anotación de layout).

## Estado
- Texto: agotado. Candidatos servidos (daiin/chol=botánico, shedy=cuerpo, ol/aiin=función).
- Falta SOLO: índice folio↔scan + correr el pipeline de visión con este protocolo.
