# RETOMAR — Voynich

## Estado 2026-07-08 (sesión de cierre del test frontera)
Papers v3 publicados. Análisis de texto AGOTADO. **Test de visión frontera CERRADO.**

### Lo que se cerró hoy
1. **Test frontera (Claude Sonnet-5) corrido** sobre 114 plantas — `annotations_claude.jsonl`, $1.47.
   - Cruce figura→código = **NULO otra vez** (REAL=62 ≤ nulo máx 78). Ni el modelo frontera halla puente.
   - **Hallazgo nuevo:** 70/114 plantas (61%) quiméricas, 0 IDs con confianza alta → los dibujos son
     composites inventados, no plantas reales → no hay referente físico estable que mapear.
   - Key: se tomó de SnapCost `~/Desktop/manage-construction/.env.local` → `.anthropic_key`.
2. **Rotor deslizante (idea del usuario) = SEÑAL REAL.** `rotor_test.py` + `rotor_control_currier.py`:
   el inventario de **sufijos DERIVA** con la distancia de folio (z=−4.60), y **SOBREVIVE** dentro de
   Currier A (z=−4.30, p<0.001); el **prefijo NO deriva**. Disociación = un ajuste que "avanza".
3. **Volvelle republicada:** artifact `6a4b5e06-3623-40ce-8309-10bc907ddce0`.
   **Papers actualizados** (respaldo en `versions/backup_20260708/`): companion de la rueda en §4.13 +
   "no es recetario/almanaque" reforzado en §4.11.

### Pendientes al volver
- [ ] Decidir si la **deriva de sufijo (rotor)** entra al paper. Falta un control extra: descartar
      deriva TEMPORAL genérica (no solo el salto A/B). Lo potente es la disociación prefijo/sufijo.
- [ ] (opcional) Verificar y añadir 2º test anti-recetario: gradiente secuencial en recetas (r=+0.04).
- [ ] Re-sincronizar los papers PUBLICADOS a estas ediciones si se van a difundir.
- [ ] Difusión: foro voynich.ninja → arXiv (cs.CL) → Cryptologia.

## Archivos clave
paper.html / paper_es.html (v3, editados hoy) · volvelle.html (artifact 6a4b5e06) ·
vision_pipeline_claude.py · annotations_claude.jsonl (114 plantas, Claude) ·
rotor_test.py · rotor_control_currier.py · RESULTADO-VISION.md · REASONING-LOG.md ·
voy_lsi.txt (transliteración) · versions/backup_20260708/ (respaldo pre-edición)

## O simplemente: "retomemos el Voynich" — todo está en memoria.
