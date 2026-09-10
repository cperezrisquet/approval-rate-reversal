# Post 2 (español) — la misma regla, distinto castigo

Post de seguimiento del paper, en español, para la audiencia local.
Publicar **4–5 días después** del primero. Sin documento adjunto; el paper
vive en el post anterior y este enlaza a aquel.

**Decisión deliberada:** la imagen y el ejemplo son **neutros** (90 % y
70 %, sin grupos reales). El mecanismo se enseña aquí; la aplicación a datos
de crédito se queda en el paper, que es donde caben sus dos advertencias.
Una imagen de redes sociales separada de sus salvedades es una cita mal
hecha esperando a ocurrir.

**Imagen:** `figures/post2_curvatura.png` (1120 × 1120, cuadrada). Se genera
con `src/figura_post_es.py`. Adjuntar como imagen única.

**Antes de publicar:** sustituir `[FECHA]` en el cuerpo por cuándo salió el
primer post.

**Texto alternativo** (LinkedIn lo pide al subir la imagen — botón "Alt"):

> Gráfico titulado "La misma regla, distinto castigo". Una curva muestra
> cuántos puntos porcentuales pierde un grupo cuando se le reduce a la mitad
> la probabilidad de pasar, según el porcentaje del que parta. La curva vale
> cero en los extremos y alcanza su máximo, unos 17 puntos, alrededor del
> 58 %. Dos puntos marcados: quien parte del 70 % pierde 16,2 puntos y quien
> parte del 90 % pierde 8,2. Al pie: la distancia entre los dos era de 20
> puntos y después de la regla es de 28; nadie los trató distinto, la brecha
> se ensanchó sola porque desde arriba se cae menos y no hay sitio por
> encima del 100 %.

Sin Markdown y sin negritas Unicode en el cuerpo.

---

## Texto del post

CIFRAS CORRECTAS, CONCLUSIONES FALSAS · 2

Dos grupos. Uno pasa el 90 % de las veces, el otro el 70 %.

Cambia la regla, idéntica para los dos: a ambos se les reduce a la mitad la
probabilidad de pasar. Sin excepciones y sin trato distinto para nadie.

El primero cae al 81,8 %: pierde 8,2 puntos.
El segundo cae al 53,8 %: pierde 16,2.

La distancia entre los dos era de 20 puntos. Ahora es de 28.

Nadie los trató distinto. La brecha se ensanchó sola, y la razón es que desde
arriba se cae menos: no hay sitio por encima del 100 %.

Esto no es un juego aritmético. Es la razón por la que una brecha medida en
puntos porcentuales no sirve para vigilar diferencias entre grupos: se
ensancha en las malas y se estrecha en las buenas sin que nadie cambie de
criterio, porque responde a de dónde parte cada uno tanto como a cómo se los
trata.

Lo medí sobre datos públicos en el paper que publiqué el [FECHA]: más de
veinte millones de solicitudes hipotecarias entre 2021 y 2023. Un solo
endurecimiento ciego al grupo, aplicado a los puntos de partida, reproduce
entre el 46 % y el 128 % de cada ensanchamiento observado.

Y dos cosas que hay que decir juntas, porque de esas cifras se sacan las dos
conclusiones y las dos están mal.

No prueban que aumentara el trato diferencial: casi todo el ensanchamiento lo
reproduce un desplazamiento que es ciego al grupo por construcción.

Y no prueban que el crédito fuera equitativo: el diseño no tiene controles de
solvencia, no compara iguales con iguales, y no dice nada sobre el nivel de
ninguna brecha. Solo sobre cómo se mueve cuando el sistema se endurece.

La regla práctica que me llevo: si vas a vigilar una diferencia entre grupos,
reporta la razón de momios con su intervalo, no la resta de porcentajes. La
resta se mueve sola.

Paper, datos y código en el post anterior.

---

## Comentario

Paper (PDF, 9 páginas), datos y código:
github.com/cperezrisquet/approval-rate-reversal

La curva de la imagen es r(1−r)(1−ψ)/(1−r+ψr), y se reproduce con
`src/figura_post_es.py`.
