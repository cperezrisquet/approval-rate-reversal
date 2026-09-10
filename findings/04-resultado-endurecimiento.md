# Resultado: H1 falsa, H3 confirmada, y con el signo al revés

Fecha: 10 de septiembre de 2026. Preregistro en
[`03-preregistro-endurecimiento.md`](03-preregistro-endurecimiento.md),
commiteado antes de calcular esto.

## H1 — FALSA

Se predijo que la caída en puntos porcentuales estaría concentrada donde la
tasa base era baja. Sobre los 28 estratos de los ocho ejes:

    correlación base 2021 vs Δ pp:  r = -0.025
    pendiente:                      -0.010 pp por pp de base

Nula. Y el diseño del test estaba mal: agrupa estratos de ejes
incomparables, y dentro se cancelan dos patrones opuestos.

Lo que hay debajo, por eje:

| Eje | Patrón |
|---|---|
| Tipo de préstamo | **Al revés de lo predicho.** Los programas con garantía pública casi no se movieron: VA −2,51 pp, RHS/FSA −2,97, FHA −3,66, contra convencional **−10,66** |
| Propósito | Sin relación con la base: cash-out −15,34 y refi −12,63 partiendo de 83–86 %, contra mejora −3,11 partiendo de 63,6 % |
| Demográficos | **Sí sigue lo predicho.** Raza: base 86,3 % → −8,89; base 72,8 % → −13,16 |

El endurecimiento se organizó por **producto y garantía**, no por la posición
del solicitante respecto al umbral. Dentro de los ejes demográficos sí
aparece el patrón de curvatura, pero es un efecto de segundo orden.

## H3 — CONFIRMADA, y sobre-predice

Contrafactual: aplicar un **único desplazamiento en momios, ciego al grupo**
(razón de momios común de Mantel-Haenszel, estimada sobre todos los estratos
del eje, no sobre el par) a las tasas base de 2021.

| Par (ambos estratos grandes) | Δ brecha obs. | Δ brecha si la política fuera ciega | Residuo |
|---|---|---|---|
| White vs Black or African American | **+3,26 pp** | **+4,15 pp** | −0,90 |
| White vs American Indian or Alaska Native | +4,43 pp | +4,35 pp | +0,09 |
| Asian vs Black or African American | +3,09 pp | +4,28 pp | −1,19 |
| Not Hispanic or Latino vs Hispanic or Latino | +3,15 pp | +2,37 pp | +0,78 |
| Male vs Female | +1,03 pp | +0,48 pp | +0,55 |

Un endurecimiento uniforme y ciego al grupo predice entre el 75 % y el 138 %
del ensanchamiento observado. En los pares de raza **sobre-predice**: la
brecha se ensanchó **menos** de lo que produce mecánicamente una política
uniforme.

### El dato más contraintuitivo

Razones de momios por estrato, 2021→2023 (más bajo = más endurecimiento):

    Black or African American   0.576
    White                       0.554
    American Indian / Alaska    0.552
    Asian                       0.544
    Native Hawaiian / Pac. Isl. 0.470

**En momios, los solicitantes negros se endurecieron algo MENOS que los
blancos** (0,576 contra 0,554). Y la brecha en puntos porcentuales se
ensanchó 3,26 pp de todas formas, por pura curvatura: la misma razón de
momios cuesta más puntos donde la base está más lejos del 100 %.

Cifras correctas, conclusión falsa: quien lee el ensanchamiento como
evidencia de más trato diferencial está leyendo un artefacto de la escala en
la que mide.

**Y al revés, con el mismo énfasis:** esto NO dice que el crédito fuera
equitativo. Dice que el ensanchamiento de la brecha en pp **no lleva
información** sobre eso. Las dos inferencias son inválidas y las dos se
hacen.

## El p-valor invierte el orden

| Eje | Breslow-Day | Rango de momios | max/min |
|---|---|---|---|
| Sex | chi2 1708,0 · log10 p **−370,9** | 0,523–0,584 | **1,115** |
| Race | chi2 234,3 · log10 p −48,8 | 0,470–0,576 | **1,224** |
| Ethnicity | chi2 134,7 · log10 p −29,2 | 0,535–0,555 | 1,037 |

El contraste declara el sexo **321 órdenes de magnitud más heterogéneo** que
la raza. La magnitud dice lo contrario: la raza dispersa más (1,224 contra
1,115). Quien use significación para decidir qué eje vigilar elige sexo
antes que raza.

Esto es el resultado del paper anterior con consecuencias reales, y no un
tecnicismo: el orden lo fija n y los grados de libertad (24,1 M y df 2
contra 21,2 M y df 4), no la sustancia.

## Lo que sigue sin poderse afirmar

No hay controles de solvencia a nivel solicitud. La API de agregaciones
**no** expone ingreso, LTV, DTI ni edad como eje de agrupación — se
comprobó: los acepta y los ignora, devolviendo el total sin desglose. Están
solo en los ficheros a nivel préstamo, de varios GB por año.

Sin esos controles no se puede decir nada causal, y el paper no debe
insinuarlo. La afirmación defendible es metodológica: sobre qué se puede y
no se puede concluir de una brecha en puntos porcentuales que se ensancha.
