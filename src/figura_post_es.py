"""
Figura cuadrada para el post 2 en español (1120 x 1120, imagen única).

El ejemplo: un dado con el MISMO sesgo — el 6 sale el 18 % de las veces en
vez del 16,67 % — contrastado con distinto número de tiradas. El sesgo no
cambia nunca; el veredicto sí. Es el resultado del paper en un objeto que
cualquiera puede imaginar.

Deliberadamente NO es un gráfico. El p-valor recorre 168 órdenes de
magnitud: en un eje logarítmico la parte legible (de 0,78 a 0,006) queda
aplastada en un sliver, y en uno lineal solo se ve la última fila. Lo que
el lector necesita son cinco filas y su veredicto, así que es una tabla.
"""
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

SURFACE, INK, INK_2 = "#fcfcfb", "#0b0b0b", "#52514e"
MUTED, GRID, BASELINE = "#898781", "#e1e0d9", "#c3c2b7"
BLUE, ORANGE = "#2a78d6", "#eb6834"

plt.rcParams.update({
    "font.family": ["Helvetica Neue", "Helvetica", "Arial", "sans-serif"],
    "svg.fonttype": "none",
})

P_TRUE, P_NULL = 0.18, 1 / 6
THROWS = [60, 600, 6_000, 60_000, 600_000]


def pvalue(n):
    """Contraste bilateral de proporción, en espacio logarítmico: pasadas
    unos cientos de miles de tiradas el p-valor hace underflow y sale 0,
    que no es un valor."""
    se = np.sqrt(P_NULL * (1 - P_NULL) / n)
    z = abs(P_TRUE - P_NULL) / se
    log10p = float(np.log(2) + stats.norm.logsf(z)) / np.log(10)
    return 10.0 ** log10p, log10p


def fmt(p, lg):
    if p >= 0.01:
        return f"{p:.2f}".replace(".", ",")
    if lg > -4:
        return f"{p:.4f}".replace(".", ",")
    mant = p / 10 ** np.floor(lg)
    return f"${mant:.0f}\\times10^{{{int(np.floor(lg))}}}$"


ROWS = [(n, *pvalue(n)) for n in THROWS]

fig = plt.figure(figsize=(11.2, 11.2), dpi=100)
fig.patch.set_facecolor(SURFACE)

fig.text(0.09, 0.955, "¿Está cargado el dado?", fontsize=46,
         fontweight="bold", color=INK, va="top")
fig.text(0.09, 0.868,
         "El 6 sale el 18 % de las veces en vez del 16,7 %.",
         fontsize=22, color=INK_2, va="top")
fig.text(0.09, 0.822,
         "El sesgo es idéntico en las cinco filas. Lo único que\n"
         "cambia es cuántas veces se tira el dado.",
         fontsize=22, color=INK, va="top", linespacing=1.4,
         fontweight="bold")

# ------------------------------------------------------------ cabecera
Y0, DY = 0.645, 0.098
XT, XP, XV = 0.09, 0.475, 0.615
for x, h, ha in ((XT, "T I R A D A S", "left"),
                 (XP, "P - V A L O R", "right"),
                 (XV, "V E R E D I C T O", "left")):
    fig.text(x, Y0 + 0.043, h, fontsize=15, color=MUTED, ha=ha,
             fontweight="bold")
fig.add_artist(plt.Line2D([0.09, 0.91], [Y0 + 0.028] * 2, color=BASELINE,
                          lw=1.6))

for i, (n, p, lg) in enumerate(ROWS):
    y = Y0 - i * DY
    loaded = p < 0.05
    fig.text(XT, y, f"{n:,}".replace(",", "."), fontsize=31, color=INK,
             va="center", fontweight="bold")
    fig.text(XP, y, fmt(p, lg), fontsize=29,
             color=BLUE if loaded else MUTED, va="center", ha="right",
             fontweight="bold")
    fig.text(XV, y, "el dado está cargado" if loaded else "no hay evidencia",
             fontsize=25, color=INK if loaded else MUTED, va="center",
             style="normal" if loaded else "italic")
    if i < len(ROWS) - 1:
        fig.add_artist(plt.Line2D([0.09, 0.91], [y - DY / 2] * 2, color=GRID,
                                  lw=1))

fig.add_artist(plt.Line2D([0.09, 0.91], [Y0 - 4.5 * DY] * 2, color=BASELINE,
                          lw=1.6))
fig.text(0.09, 0.165,
         "Mismo dado. Mismo sesgo. El p-valor no mide lo cargado\n"
         "que está: mide cuántas veces lo tiraste.",
         fontsize=24, color=INK, va="top", linespacing=1.4,
         fontweight="bold")
fig.text(0.09, 0.048,
         "Contraste bilateral de proporción · Cifras correctas, "
         "conclusiones falsas · 2",
         fontsize=15, color=MUTED, va="top")

OUT = pathlib.Path(__file__).resolve().parent.parent / "figures"
for ext in ("png", "svg"):
    fig.savefig(OUT / f"post2_dado.{ext}", facecolor=SURFACE)
print("  figures/post2_dado.png  (1120 x 1120)")
for n, p, lg in ROWS:
    print(f"    {n:>9,} tiradas -> p = {p:.3g}   (log10 {lg:.1f})")
