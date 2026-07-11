# Tanda 12 — Caso f2r y test "¿son números?" (2026-07-10)

Estado: **hecho en sesión, aún NO integrado al paper**. Este archivo persiste los hallazgos para que no vivan solo en memoria.

## 1. Descarga y verificación de imagen real (f2r)
- Bajé el escaneo real de f2r desde voynich.ninja: `/browser/i/2000/1006078.jpg` → `foro_images/f2r_1006078.jpg` (+ flyleaf `1006075`).
- Recortes de trabajo: `foro_images/ptop.jpg` (párrafo superior), `crop_L1.jpg`, `z_L1a.jpg`, `z_L1b.jpg`.

## 2. Validación de la transcripción Takahashi contra el escaneo
- Comparé glifo por glifo el párrafo superior de f2r contra la transliteración Takahashi.
- **Resultado: fiel.** Las únicas discrepancias son dudas de ±1 *minim* (trazos verticales ambiguos, el problema clásico de i/ii/iii), no errores de lectura.
- Consecuencia: podemos confiar en la transcripción como sustrato; las conclusiones del paper no dependen de un error de transcripción.

## 3. Descomposición del párrafo superior
- Los prefijos dominantes del párrafo son `ch-`, `cth-`, `ckh-`, `sh-`.
- Son exactamente los prefijos **herbales**: la página **se auto-declara herbaria** por su vocabulario, consistente con el dibujo de planta.

## 4. Test "¿son números?" (intuición del usuario) → **NO**
Dos pruebas independientes, ambas en contra de la hipótesis numeral:

- **Benford NO discrimina.** La ley de Benford la pasa igual un texto azaroso; no separa "es numeral" de "no lo es". Prueba nula por diseño → descartada como evidencia.
- **Alfabetos por-posición disjuntos + información mutua.** En un sistema numeral posicional los mismos dígitos reaparecen en todas las posiciones (dígito ⟂ posición → información mutua ≈ 0). En Voynich los inventarios por posición son casi disjuntos: **I(glifo;posición) = 0.72** vs **0.014** de un numeral de referencia → los glifos están **~50× más atados a su posición** que en un sistema de números. No es notación numérica posicional.

## 5. Modelo del usuario que SÍ calza
- Código **[categoría][valor]**, tipo `hmb55` = "hombre mayor bueno 55".
- Encaja con la lectura a-priori / la intuición de Friedman: estructura ranurada (slots) donde cada posición codifica una dimensión distinta, no un dígito. Consistente con el hallazgo del paper de que las posiciones portan información distinta (alfabetos disjuntos) y con el "rotor deslizante" (deriva de sufijo por distancia de folio).

## Pendiente
- Decidir si f2r entra al paper como **figura/apéndice** (caso de validación de imagen real) — ver `TANDA12` en el plan de sesión.
- Los puntos 2–4 son citables en §4 (integridad de datos / test numeral-nulo).
