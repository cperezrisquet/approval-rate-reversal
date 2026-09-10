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

import statistics

from analysis import (decompose, homogeneity, homogeneity_log10p, or_spread,
                      pooled_rate, rate_change_spread, scaled,
                      stratum_odds_ratios)
from application_data import AXIS_LABELS, PAIRS, SEGMENTATIONS, pair, rate

P05 = np.log10(0.05)

print("Generando figuras:")

# =========================================================== FIGURA 2
# (se define primero porque la portada la reutiliza sin título)
# Change-over-a-continuum, dos series, una sola escala -> línea.
# El eje y es log10(p) y no p: a escala real el p-valor hace underflow, y
# graficar un cero que en realidad es 1e-399 sería mentir con el eje.
# La portada del PDF usa la misma figura sin título propio.
SCALES = [30000, 10000, 3000, 1000, 300, 100, 30, 10, 3, 1]
DEMO = [("loan_purposes", "Loan purpose", BLUE),
        ("sexes", "Sex", ORANGE)]


def _curve(var):
    t0, t1 = pair(var, 2024, 2025)
    out = []
    for div in SCALES:
        a0, a1 = scaled(t0, div), scaled(t1, div)
        n = sum(v[0] for v in a0.values()) + sum(v[0] for v in a1.values())
        lg, _, _ = homogeneity_log10p(a0, a1)
        out.append((n, lg))
    return out


CURVES = {var: _curve(var) for var, _, _ in DEMO}


def fig1(title=True, height=3.15):
    fig, ax = plt.subplots(figsize=(6.4, height))
    floor = -12.0                      # el eje se corta aquí, no los datos

    ax.axhspan(P05, 1.0, color=AQUA, alpha=0.06, zorder=0)
    ax.axhline(P05, color=BASELINE, lw=1, ls=(0, (4, 3)), zorder=1)
    ax.annotate("p = 0.05", (2.4e7, P05), xytext=(0, -11),
                textcoords="offset points", color=MUTED, fontsize=8,
                ha="right")
    ax.annotate("nothing detected above this line", (5.5e2, P05 + 0.35),
                color=MUTED, fontsize=8, style="italic", va="bottom")

    for var, label, colour in DEMO:
        pts = CURVES[var]
        xs = [n for n, _ in pts]
        ys = [max(lg, floor - 3) for _, lg in pts]      # recorte de dibujo
        ax.plot(xs, ys, color=colour, lw=2, zorder=3)
        vis = [(n, lg) for n, lg in pts if lg >= floor]
        ax.scatter([n for n, _ in vis], [lg for _, lg in vis], s=32,
                   facecolor=colour, edgecolor=SURFACE, lw=1.5, zorder=4)
        # Etiqueta directa donde la curva tiene sitio: para la azul, en
        # plena caída (junto al borde inferior chocaba con la flecha).
        if colour is BLUE:
            nx, ny = min(vis, key=lambda p: abs(p[1] + 3.0))
            off, ha = (-10, 2), "right"
        else:
            nx, ny = vis[-1]
            off, ha = (6, 9), "left"
        ax.annotate(label, (nx, ny), xytext=off, textcoords="offset points",
                    color=colour, fontsize=9, fontweight="bold", ha=ha)

    # Dónde acaba de verdad la curva azul, que es el remate del argumento.
    full = CURVES["loan_purposes"][-1]
    ax.annotate(f"at full scale: p ≈ 10$^{{{full[1]:.0f}}}$",
                (full[0], floor), xytext=(-6, 26), textcoords="offset points",
                color=BLUE, fontsize=8.5, ha="right", fontweight="bold",
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.1,
                                shrinkA=2, shrinkB=1))

    ax.set_xscale("log")
    ax.set_xlabel("Applications counted (both years)")
    ax.set_ylabel("log$_{10}$ of the Breslow–Day p-value")
    ax.set_ylim(floor, 1.0)
    clean(ax)
    ax.legend(handles=[
        plt.Line2D([], [], color=c, lw=2, marker="o", ms=5.5,
                   markeredgecolor=SURFACE, markeredgewidth=1.5, label=l)
        for _, l, c in DEMO], loc="lower left", frameon=False, fontsize=8.5)
    if title:
        ax.set_title("The same data, counted at different scales",
                     loc="left", fontsize=10.5, fontweight="bold", pad=9)
    fig.tight_layout()
    return fig


save(fig1(), "fig2_scale")
save(fig1(title=False, height=3.75), "fig_cover")

# =========================================================== FIGURA 1
# 56 pares: ¿explica la composición el movimiento agregado? Dos magnitudes
# comparables en las mismas unidades -> dispersión con la diagonal y=x como
# referencia. Si la mezcla lo explicara todo, los puntos irían sobre ella.
ROWS = []
for var in SEGMENTATIONS:
    for y0, y1 in PAIRS:
        t0, t1 = pair(var, y0, y1)
        if len(t0) < 2:
            continue
        r0, r1 = pooled_rate(t0.values()), pooled_rate(t1.values())
        within, mix = decompose(t0, t1)
        ROWS.append(dict(var=var, pooled=(r1 - r0) * 100, mix=mix * 100,
                         within=within * 100,
                         spread=rate_change_spread(t0, t1)[2] * 100,
                         ors=or_spread(t0, t1),
                         p=homogeneity(t0, t1)[1]))


def fig2():
    fig, ax = plt.subplots(figsize=(4.75, 4.15))
    lim = 8.0
    ax.plot([-lim, lim], [-lim, lim], color=BASELINE, lw=1, ls=(0, (4, 3)),
            zorder=1)
    ax.annotate("if composition\nexplained it all", (-4.6, -4.6),
                xytext=(10, -3), textcoords="offset points", color=MUTED,
                fontsize=8, style="italic", va="top")
    ax.axhspan(-0.5, 0.5, color=BLUE, alpha=0.06, zorder=0)
    ax.axhline(0, color=BASELINE, lw=1, zorder=1)

    pre = [r for r in ROWS if r["var"] == "loan_purposes"]
    rest = [r for r in ROWS if r["var"] != "loan_purposes"]
    ax.scatter([r["pooled"] for r in rest], [r["mix"] for r in rest],
               s=34, facecolor=MUTED, alpha=0.55, edgecolor=SURFACE, lw=1,
               zorder=3, label=f"other seven axes  (n={len(rest)})")
    ax.scatter([r["pooled"] for r in pre], [r["mix"] for r in pre],
               s=52, facecolor=BLUE, edgecolor=SURFACE, lw=1.5, zorder=4,
               label=f"loan purpose — pre-registered  (n={len(pre)})")

    inside = sum(1 for r in ROWS if abs(r["mix"]) < 0.5)
    ax.annotate(f"{inside} of {len(ROWS)} pairs\ninside ±0.5 pp",
                (-lim, 0.5), xytext=(6, 10), textcoords="offset points",
                color=INK_2, fontsize=8.5, fontweight="bold")

    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
    ax.set_xlabel("Change in the pooled approval rate (pp)")
    ax.set_ylabel("Composition component (pp)")
    ax.set_aspect("equal")
    clean(ax)
    ax.legend(loc="upper left", bbox_to_anchor=(-0.02, 0.85),
              frameon=False, fontsize=8)
    ax.set_title("Composition does not move the pooled rate",
                 loc="left", fontsize=10.5, fontweight="bold", pad=9)
    fig.tight_layout()
    return fig


save(fig2(), "fig1_composition")

# =========================================================== FIGURA 3
# Una sola medida sobre ocho categorías, con intervalo -> dot plot con
# rango, ordenado. Un solo tono: el trabajo es magnitud, no identidad.
def fig3():
    fig, ax = plt.subplots(figsize=(6.4, 3.25))
    axes = []
    for var in SEGMENTATIONS:
        g = [r for r in ROWS if r["var"] == var]
        ors = [r["ors"] for r in g if r["ors"]]
        axes.append((AXIS_LABELS[var], min(ors), max(ors),
                     sum(1 for r in g if r["p"] >= 0.05), len(g)))
    axes.sort(key=lambda a: a[2])

    ys = range(len(axes))
    ax.axvline(1.0, color=BASELINE, lw=1, zorder=1)
    ax.annotate("1× — every stratum moves alike", (1.0, -0.62),
                xytext=(4, 0), textcoords="offset points", color=MUTED,
                fontsize=8, style="italic", va="center")
    for y, (name, lo, hi, ns, k) in zip(ys, axes):
        ax.plot([lo, hi], [y, y], color=BLUE, lw=2.6, alpha=0.30,
                solid_capstyle="round", zorder=2)
        ax.scatter([lo], [y], s=42, facecolor=SURFACE, edgecolor=BLUE,
                   lw=1.8, zorder=4)
        ax.scatter([hi], [y], s=52, facecolor=BLUE, edgecolor=SURFACE,
                   lw=1.5, zorder=4)
        ax.annotate(f"{hi:.2f}×", (hi, y), xytext=(8, 0),
                    textcoords="offset points", color=INK, fontsize=8.5,
                    va="center", fontweight="bold")
        if ns:
            # A la derecha de la cifra: a la izquierda chocaba con el
            # nombre del eje.
            ax.annotate(f"— Breslow–Day fails to reject in {ns} of {k}",
                        (hi, y), xytext=(46, 0), textcoords="offset points",
                        color=ORANGE, fontsize=7.8, va="center")
    ax.set_yticks(list(ys)); ax.set_yticklabels([a[0] for a in axes])
    ax.set_xlim(0.95, 2.62)
    ax.set_ylim(-1.1, len(axes) - 0.4)
    ax.set_xlabel("Spread of stratum odds ratios, max ÷ min  (7 year-pairs)")
    clean(ax, keep_left=False)
    ax.grid(axis="y", visible=False)
    ax.set_title("How much heterogeneity each axis actually carries",
                 loc="left", fontsize=10.5, fontweight="bold", pad=9)
    fig.tight_layout()
    return fig


save(fig3(), "fig3_axes")

# =========================================================== FIGURA 4
# Dos cantidades en unidades distintas -> dos paneles, nunca dos ejes y.
# Es la figura del matiz. Solo `races`: meter etnia en el mismo eje de
# categorías daba un "rango" que cruzaba dos segmentaciones distintas y no
# significaba nada. Los números de etnia van en el pie de figura.
SHORT = {"Native Hawaiian or Other Pacific Islander": "Native Hawaiian / Pac. Isl.",
         "American Indian or Alaska Native": "Am. Indian / Alaska Native"}


def fig4():
    t0, t1 = pair("races", 2024, 2025)
    cats = sorted(t1, key=lambda k: -rate(*reversed(t1[k])))
    levels = [rate(*reversed(t1[s])) * 100 for s in cats]
    moves = [(rate(*reversed(t1[s])) - rate(*reversed(t0[s]))) * 100
             for s in cats]
    ys = list(range(len(cats)))[::-1]

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(6.4, 2.55),
                                   gridspec_kw={"wspace": 0.08})
    for ax, vals, colour, lbl, lo in (
            (axL, levels, BLUE, "Approval rate, 2025 (%)", 60),
            (axR, moves, ORANGE, "Change 2024→2025 (pp)", 0)):
        for y, v in zip(ys, vals):
            ax.plot([lo, v], [y, y], color=GRID, lw=0.8, zorder=1)
            ax.scatter([v], [y], s=46, facecolor=colour, edgecolor=SURFACE,
                       lw=1.4, zorder=3)
            ax.annotate(f"{v:.1f}", (v, y), xytext=(7, 0),
                        textcoords="offset points", color=INK_2, fontsize=8,
                        va="center")
        ax.annotate(f"spread {max(vals) - min(vals):.1f} pp", (0.5, 1.04),
                    xycoords="axes fraction", ha="center", color=colour,
                    fontsize=9, fontweight="bold")
        ax.set_xlabel(lbl, fontsize=8.5)
        clean(ax, keep_left=False)
        ax.grid(axis="y", visible=False)
        ax.set_yticks(ys)
        ax.set_ylim(-0.7, len(cats) - 0.3)

    axL.set_xlim(60, 90)
    axR.set_xlim(0, 4.4)
    axL.set_yticklabels([SHORT.get(s, s) for s in cats], fontsize=8)
    axR.set_yticklabels([])
    fig.suptitle("Levels differ. The year-over-year movement does not.",
                 x=0.012, ha="left", fontsize=10.5, fontweight="bold", y=0.99)
    fig.subplots_adjust(top=0.78, bottom=0.19, left=0.24, right=0.97)
    return fig


save(fig4(), "fig4_levels")

print("\nListo.")
