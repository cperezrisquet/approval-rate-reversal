# Preregistro — ¿a quién se le apretó en 2021-2023?

**Escrito y commiteado ANTES de calcular nada de lo que sigue.** El commit
que lo introduce es anterior al que trae los resultados; el historial de git
es la prueba.

Fecha: 10 de septiembre de 2026.

## El hecho que hay que explicar

La tasa de aprobación agrupada de HMDA cayó **9,38 pp** entre 2021 y 2023
(84,30 % → 74,92 %). La descomposición exacta ya calculada la reparte así:

| Componente | Aporte |
|---|---|
| Intra-estrato (endurecimiento) | **−7,61 pp** |
| Mezcla (rotación de producto) | −1,77 pp |

El término intra-estrato es cuatro veces la mezcla y está sin explicar. Es el
número más grande del conjunto de datos.

## El mecanismo que se postula

Un prestamista no aprieta en puntos porcentuales: mueve un corte de score, o
un umbral de DTI, o un mínimo de LTV. **Eso es un desplazamiento en momios,
no en puntos porcentuales.** Y un mismo desplazamiento en momios produce
caídas en puntos porcentuales muy distintas según dónde esté cada grupo:

- un grupo que aprueba al 88 % pierde pocos puntos,
- un grupo que aprueba al 65 % pierde muchos.

La curva es más plana cerca del 100 % y más empinada en el medio. Es
aritmética, no política.

## Hipótesis

**H1.** La caída en puntos porcentuales 2021→2023 está **negativamente**
correlacionada con la tasa base de 2021 entre estratos: donde la base era
baja, la caída es mayor.

**H2 (la que importa).** Por tanto, la **brecha en puntos porcentuales entre
grupos se ensancha** durante un endurecimiento, y el ensanchamiento es
predecible a partir de las tasas base y de un único desplazamiento común en
momios. No hace falta ningún trato diferencial para producirlo.

**H3.** El contraste que decide si un endurecimiento fue uniforme *en momios*
es el de Breslow-Day sobre el par 2021→2023. Si no rechaza, un solo
desplazamiento común explica lo observado para ese eje. Si rechaza, hay algo
más que un desplazamiento uniforme.

## Predicciones falsables

1. Correlación negativa entre tasa base 2021 y Δ pp 2021→2023, sobre los
   estratos de todos los ejes disponibles.
2. La brecha máximo-mínimo en pp crece de 2021 a 2023 en los ejes con base
   dispersa (raza), y crece poco o nada en los de base compacta (sexo).
3. El ensanchamiento observado quedará **próximo** al que predice aplicar la
   razón de momios común de Mantel-Haenszel a las tasas base de 2021. La
   distancia entre lo observado y esa predicción es lo que NO explica un
   desplazamiento uniforme.

Si (1) sale plana o positiva, el mecanismo postulado es falso y hay que
publicarlo como tal, igual que se publicó el fallo de la hipótesis anterior
en `01-hipotesis-preregistrada.md`.

## Lo que este diseño NO puede afirmar

Con tablas cruzadas agregadas y sin variables de solvencia a nivel
solicitud, **no se puede decir nada sobre discriminación**, ni en un sentido
ni en el otro. No hay controles de ingreso, LTV, DTI, score ni geografía a
nivel individual, y HMDA no publica score.

Lo que sí se puede establecer es metodológico, y es el objeto del paper:

- si el ensanchamiento observado de una brecha es o no compatible con un
  único desplazamiento en momios;
- cuánta parte del ensanchamiento en pp está mecánicamente implicada por las
  tasas base;
- y por tanto, que **inferir trato diferencial a partir de una brecha en pp
  que se ensancha no es válido** — ni tampoco inferir equidad a partir de una
  política uniforme.

Las dos inferencias son incorrectas, y las dos se hacen. Eso es el paper: la
serie trata exactamente de cifras correctas leídas como conclusiones falsas.

## Ejes a usar

Los ocho ya versionados, más los de riesgo de crédito que la API exponga
(tramos de ingreso, LTV, DTI) si existen como eje de agrupación. Se
reportará la distribución completa sobre todos los ejes disponibles, nunca
el eje que dé el resultado más llamativo.
