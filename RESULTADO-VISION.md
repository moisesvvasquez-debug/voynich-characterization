# Resultado del piloto de visión (madrugada 2026-07-08)

## Qué corrió
Pipeline completo, autónomo: **113/114 plantas herbales** descritas por Qwen2.5-VL (local, $0).
Mapeo folio↔scan determinista **verificado** (f20r=scan39, f45r=scan89). Cruce + prueba de permutación.

## Resultado: NULO (honesto, sin adornos)
- El cruce aparentaba **72 "señales fuertes"** (palabras cuyas plantas comparten un rasgo).
- **Prueba de permutación:** barajando features al azar salen **62 (rango 42-81)**. Las 72 reales caen DENTRO de ese rango → **es ruido, no señal.**
- **NO se detectó puente figura→código.** Las palabras discriminantes (pchor, otcho…) NO marcan un rasgo de planta compartido por encima del azar.

## Por qué (la causa importa)
1. **El modelo 7B es demasiado grueso:** llama "pinnada" al **73%** de las hojas y parte las raíces ~50/50 taproot/fibrous. Baja resolución = baja capacidad de discriminar.
2. **n chico:** 4-5 plantas por palabra.
3. Métrica de "lift" ruidosa con rasgos raros (1 planta bulbosa = lift 11x, sin sentido).

## Qué significa (y qué NO)
- **NO podemos concluir "no existe puente".** El modelo pudo ser demasiado débil para verlo — es el **falso negativo** que se advirtió desde el principio (modelo débil → riesgo de perder señal, no de inventarla).
- Sobre tu pregunta (¿`daiin` = parte física o esencia/alma?): **INCONCLUSO.** El nulo no dice "esencia" limpio, porque el modelo tampoco podría haber detectado el mapeo físico si lo hubiera.

## Lo valioso que SÍ quedó
- **El pipeline entero FUNCIONA** (prueba de concepto): descarga → describe → mapea folios → cruza → valida con permutación. Todo autónomo, reproducible, $0.
- Sabemos exactamente qué falla y qué se necesita.

## Próximo paso real (test justo)
Re-correr con un **vision-LLM frontera** (GPT-4o / Claude / Gemini / Qwen-VL-72B, ~$1-3 total) + **categorías morfológicas más finas** (no solo taproot/fibrous/pinnate) + estadística estricta (n≥5, permutación). El pipeline ya está armado — solo cambiar el modelo (y usar API en vez de Ollama local para el 72B).

Archivos: `annotations.jsonl` (113 descripciones), `vision_pipeline.py`, `pipeline.log`.
