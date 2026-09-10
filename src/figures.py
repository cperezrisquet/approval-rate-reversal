"""Figuras del paper. Paleta de referencia dataviz, modo claro."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from application_data import *

# ---------------------------------------------------------------- tokens
SURFACE   = "#fcfcfb"
INK       = "#0b0b0b"
INK_2     = "#52514e"
MUTED     = "#898781"
GRID      = "#e1e0d9"
BASELINE  = "#c3c2b7"
BLUE      = "#2a78d6"   # slot 1
ORANGE    = "#eb6834"   # slot 2
AQUA      = "#1baf7a"   # slot 3
RED       = "#e34948"   # slot 8 / diverging pole

plt.rcParams.update({
    "font.family": ["Helvetica Neue", "Helvetica", "Arial", "sans-serif"],
    "font.size": 9,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "axes.edgecolor": BASELINE,
    "axes.labelcolor": INK_2,
    "axes.titlecolor": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "text.color": INK,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.6,
    "axes.axisbelow": True,
    "svg.fonttype": "none",
})

import pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
FIGDIR = ROOT / "figures"
FIGDIR.mkdir(exist_ok=True)

def clean(ax, keep_left=True):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(BASELINE)
    if keep_left:
        ax.spines["left"].set_color(BASELINE)
    else:
        ax.spines["left"].set_visible(False)

def save(fig, name):
    fig.savefig(FIGDIR / f"{name}.svg", format="svg", bbox_inches="tight",
                facecolor=SURFACE)
    fig.savefig(FIGDIR / f"{name}.png", format="png", bbox_inches="tight",
                facecolor=SURFACE, dpi=150)
    plt.close(fig)
    print(f"  figures/{name}.svg")

print("Generando figuras:")

# =========================================================== FIGURA 1
# La reversión. Dos lecturas de la misma tasa -> escala única, indexado o
# puntos porcentuales. La portada del PDF necesita esta misma figura sin
# título propio, así que se construye por función (igual que en la #1).
def fig1(title=True, height=3.05):
    fig, ax = plt.subplots(figsize=(6.4, height))
    # TODO: tasa agrupada vs. tasa dentro de cada segmento.
    clean(ax)
    if title:
        ax.set_title("TODO: pooled rate falls, every segment rises",
                     loc="left", fontsize=10.5, fontweight="bold", pad=9)
    fig.tight_layout()
    return fig

save(fig1(), "fig1_reversal")
save(fig1(title=False, height=2.72), "fig1_cover")

# =========================================================== FIGURA 2
# Descomposición: componente intra-segmento vs. componente de mezcla.
# Part-to-whole con signo -> barras apiladas divergentes desde 0.
def fig2():
    fig, ax = plt.subplots(figsize=(6.4, 2.9))
    # TODO
    clean(ax)
    fig.tight_layout()
    return fig

save(fig2(), "fig2_decomposition")

# =========================================================== FIGURA 3
# Frecuencia de la reversión por segmentación y período. Matriz -> heatmap
# con escala divergente centrada en "no revierte".
def fig3():
    fig, ax = plt.subplots(figsize=(6.4, 3.1))
    # TODO
    clean(ax)
    fig.tight_layout()
    return fig

save(fig3(), "fig3_scan")

# =========================================================== FIGURA 4
# Tasa estandarizada junto a las dos lecturas publicadas. Comparación de
# magnitudes -> barras horizontales ordenadas.
def fig4():
    fig, ax = plt.subplots(figsize=(6.4, 2.6))
    # TODO
    clean(ax, keep_left=False)
    fig.tight_layout()
    return fig

save(fig4(), "fig4_standardized")

print("\nListo.")
