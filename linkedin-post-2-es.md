# Post 2 (español) — el dado cargado

Post de seguimiento del paper, en español, para la audiencia local.
Publicar **4–5 días después** del primero para que no compitan por la misma
audiencia. Sin documento adjunto; el paper vive en el post anterior, y este
enlaza a aquel.

**Imagen:** `figures/post2_dado.png` (1120 × 1120, cuadrada). Se genera con
`src/figura_post_es.py`. Adjuntar como imagen única.

**Texto alternativo** (LinkedIn lo pide al subir la imagen — botón "Alt"):

> Tabla titulada "¿Está cargado el dado?". El 6 sale el 18 % de las veces
> en vez del 16,7 %; el sesgo es idéntico en las cinco filas y lo único que
> cambia es cuántas veces se tira. Con 60 tiradas el p-valor es 0,78 y el
> veredicto es "no hay evidencia". Con 600 tiradas, 0,38, tampoco hay
> evidencia. Con 6.000 tiradas el p-valor baja a 0,0056 y el veredicto pasa
> a "el dado está cargado". Con 60.000 tiradas es 2 por 10 elevado a −18, y
> con 600.000 tiradas es 5 por 10 elevado a −169; en ambos casos el dado
> está cargado. Al pie: mismo dado, mismo sesgo; el p-valor no mide lo
> cargado que está, mide cuántas veces lo tiraste.

Sin Markdown y sin negritas Unicode en el cuerpo.

---

## Texto del post

CIFRAS CORRECTAS, CONCLUSIONES FALSAS · 2

Tengo un dado ligeramente cargado. El 6 sale el 18 % de las veces en vez del
16,7 % que le tocaría.

Si lo tiro 60 veces y le corro un test, el resultado es p = 0,78: no hay
evidencia de que esté cargado. Si lo tiro 600.000 veces, el mismo dado da un
p-valor con 168 ceros detrás de la coma.

El dado no cambió. El sesgo tampoco. Solo cambió cuántas veces lo tiré.

Esto no es un tecnicismo de laboratorio. Es la razón por la que dos áreas de
una misma empresa pueden mirar el mismo comportamiento y no ponerse de
acuerdo en si "hay diferencia".

El área con más volumen siempre va a encontrar diferencias significativas,
porque a partir de cierto tamaño de muestra cualquier diferencia lo es. El
área con menos volumen nunca las va a encontrar, aunque estén ahí. Y las dos
van a tener razón según su propio test.

Lo verifiqué con datos públicos en el paper que publiqué la semana pasada:
17,9 millones de solicitudes de crédito hipotecario. El test de homogeneidad
da p cercano a 10 elevado a −399. Los mismos datos, contados a la milésima
parte de escala, dan p = 0,73.

Lo que sí se puede reportar sin que dependa del volumen es la magnitud. En
ese caso, cuánto se diferencian entre sí los segmentos: un cociente, no un
p-valor. Con esa medida los ocho cortes que probé se separan por un factor
de quince, y el orden no es el que uno esperaría.

La regla práctica que me llevo:

Si alguien te trae un p-valor sin decirte sobre cuántos registros lo calculó,
no te trajo un resultado. Te trajo el tamaño de su tabla.

Paper completo, datos y código en el primer comentario del post anterior.

---

## Comentario

Paper (PDF, 9 páginas), datos y código:
github.com/cperezrisquet/approval-rate-reversal

El dado de la imagen se reproduce con `src/figura_post_es.py`.
