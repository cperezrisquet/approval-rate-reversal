"""
Figura cuadrada para el post 2 en español (1120 x 1120, imagen única).

Enseña SOLO el mecanismo, con dos anclas neutras (90 % y 70 %) y un cambio
de regla idéntico para ambas: los momios a la mitad. La aplicación a datos
de crédito se queda en el paper, que es donde caben las advertencias.
Meterla en una imagen de redes sociales, separada de sus dos salvedades,
es pedir que se cite mal.
"""
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

SURFACE, INK, INK_2 = "#fcfcfb", "#0b0b0b", "#52514e"
MUTED, GRID, BASELINE = "#898781", "#e1e0d9", "#c3c2b7"
BLUE, ORANGE = "#2a78d6", "#eb6834"

plt.rcParams.update({
    "font.family": ["Helvetica Neue", "Helvetica", "Arial", "sans-serif"],
    "svg.fonttype": "none",
})

PSI = 0.5            # "los momios a la mitad", igual para los dos
A, B = 0.90, 0.70    # las dos anclas


def after(r, psi=PSI):
    o = r / (1 - r)
    return psi * o / (1 + psi * o)


def cost(r, psi=PSI):
    return r - after(r, psi)


fig = plt.figure(figsize=(11.2, 11.2), dpi=100)
fig.patch.set_facecolor(SURFACE)
ax = fig.add_axes([0.115, 0.335, 0.845, 0.375])
ax.set_facecolor(SURFACE)

xs = np.linspace(0.02, 0.985, 400)
ax.plot(xs * 100, [cost(x) * 100 for x in xs], color=INK_2, lw=3.2, zorder=3)
for r in (A, B):
    ax.scatter([r * 100], [cost(r) * 100], s=260, facecolor=BLUE,
               edgecolor=SURFACE, lw=4, zorder=5)
    ax.annotate(f"parte del {r*100:.0f} %\npierde {cost(r)*100:.1f} puntos",
                (r * 100, cost(r) * 100), xytext=(-16, -14),
                textcoords="offset points", color=BLUE, fontsize=19,
                fontweight="bold", ha="right", va="top", linespacing=1.4)

ax.set_xlim(0, 100)
ax.set_ylim(0, 21)
ax.set_xlabel("De qué porcentaje partes", fontsize=20, color=INK_2, labelpad=12)
ax.set_ylabel("Puntos que pierdes", fontsize=20, color=INK_2, labelpad=12)
ax.tick_params(labelsize=17, colors=MUTED)
ax.grid(True, color=GRID, lw=0.9)
ax.set_axisbelow(True)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
for s in ("bottom", "left"):
    ax.spines[s].set_color(BASELINE)

fig.text(0.09, 0.955, "La misma regla,\ndistinto castigo", fontsize=46,
         fontweight="bold", color=INK, va="top", linespacing=1.15)
fig.text(0.09, 0.795,
         "A los dos se les reduce a la mitad la probabilidad de pasar.\n"
         "Exactamente la misma regla, sin excepciones para nadie.",
         fontsize=21, color=INK_2, va="top", linespacing=1.5)

g0, g1 = (A - B) * 100, (after(A) - after(B)) * 100
fig.text(0.09, 0.255,
         f"La distancia entre los dos era de {g0:.0f} puntos.\n"
         f"Después de la regla es de {g1:.0f}.",
         fontsize=26, color=INK, va="top", linespacing=1.45,
         fontweight="bold")
fig.text(0.09, 0.145,
         "Nadie los trató distinto. La brecha se ensanchó sola, porque\n"
         "desde arriba se cae menos: no hay sitio por encima del 100 %.",
         fontsize=20, color=INK_2, va="top", linespacing=1.5)
fig.text(0.09, 0.036,
         "Cifras correctas, conclusiones falsas · 2",
         fontsize=15, color=MUTED, va="top")

OUT = pathlib.Path(__file__).resolve().parent.parent / "figures"
for ext in ("png", "svg"):
    fig.savefig(OUT / f"post2_curvatura.{ext}", facecolor=SURFACE)
print("  figures/post2_curvatura.png  (1120 x 1120)")
print(f"    {A*100:.0f}% -> {after(A)*100:.1f}%   pierde {cost(A)*100:.2f} pp")
print(f"    {B*100:.0f}% -> {after(B)*100:.1f}%   pierde {cost(B)*100:.2f} pp")
print(f"    brecha {g0:.1f} -> {g1:.1f} pp   (+{g1-g0:.1f})")
