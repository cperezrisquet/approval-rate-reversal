# Resultado: NO revierte. Ni en HMDA ni en ProUsuario.

Fecha de la comprobación: 10 de septiembre de 2026.

## Hipótesis preregistrada: falsa

Ver `01-hipotesis-preregistrada.md`. La predicción era componente de mezcla
negativo y mayor en magnitud que el intra-estrato, por el desplazamiento de
compra hacia refinanciación.

HMDA nacional (51 jurisdicciones), 2024 → 2025, segmentado por loan_purpose:

    TASA AGRUPADA   75.95%  ->  77.61%   +1.67 pp
    componente intra-estrato  +1.74 pp
    componente de mezcla      -0.07 pp     <- la predicción falla aquí

La composición apenas se movió. Cinco de seis propósitos suben, la tasa
agrupada sube, y no hay contradicción que explicar.

## Barrido completo: 0 de 56

8 segmentaciones (loan_purpose, loan_type, lien_status, construction_method,
total_units, race, sex, ethnicity) x 7 pares de años consecutivos (2018-2025).
Datos en `scan-hmda-56-pares.json`, script en `scan_hmda.py`.

| | |
|---|---|
| pares probados | 56 |
| **reversión unánime (Simpson)** | **0** |
| mayoría del peso contra el agregado | 2 |
| al menos un estrato contra el agregado | 16 |

El componente de mezcla se queda por debajo de 0,2 pp en casi todos los
pares, contra movimientos agregados de 1 a 6,5 pp. En estas cifras la tasa
de aprobación se mueve por comportamiento dentro de los estratos, no por
composición de la demanda.

El par más cercano es loan_purpose 2020 → 2021: 5 de 6 estratos se mueven
contra el agregado, con 62,6 % del peso. Pero el cambio agregado es de
-0,03 pp, indistinguible de cero: eso no es una reversión de signo, es ruido
alrededor de cero, y presentarlo como hallazgo sería el propio anti-patrón
que la serie denuncia.

## ProUsuario (RD): tampoco

`data/prousuario_reclamaciones_2020-2026.csv`, script en
`scan_prousuario.py`. Tasa = Favorable / (Favorable + Desfavorable),
estratos = sexo, mensual desde agosto de 2020.

| | |
|---|---|
| pares anuales | 6 → **0 reversiones** |
| pares mensuales consecutivos | 70 → **0 reversiones** |
| mayoría del peso contra el agregado (mensual) | 12 |

Además solo trae un eje de segmentación (sexo). Sin institución y sin tipo
de reclamación, no da para el barrido que el paper necesita.

## Lo que SÍ sale, y podría ser el paper

Breslow-Day sobre HMDA 2024 → 2025 por loan_purpose:

    chi2 = 1855.9    p ~ 0

Las razones de momios de los estratos **no son homogéneas**, y por goleada.
Es decir: la tasa agrupada no es un resumen válido de los estratos —no
porque se invierta, sino porque no hay un efecto común que resumir. Es un
argumento más fuerte y menos anecdótico que la reversión de signo, y se
sostiene con los datos ya bajados.

Reencuadre posible: en vez de "la paradoja que acecha a tu tasa de
aprobación", el paper sería "la paradoja no aparece, y el motivo por el que
la tasa agrupada igual no sirve es otro". Eso exige reescribir la tesis,
no solo rellenar huecos.

## Lo que NO se ha mirado

Nivel prestamista (`leis`) y estratos finos de crédito (tramos de ingreso,
LTV, DTI). Ahí es más probable que aparezcan reversiones, pero "algún
prestamista revierte" es un hallazgo débil, y buscarlo sin preregistrar la
hipótesis es exactamente el error contra el que argumenta la serie.
