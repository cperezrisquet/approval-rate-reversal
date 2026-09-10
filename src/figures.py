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

from analysis import (GAP_PAIRS, Y0, Y1, curvature_cost, gap_counterfactual,
                      homogeneity_log10p, mantel_haenszel_or, odds_shift,
                      stratum_or_ci)
from application_data import AXIS_LABELS, pair, rate

SHORT = {"Black or African American": "Black or African Am.",
         "American Indian or Alaska Native": "Am. Indian / Alaska Nat.",
         "Native Hawaiian or Other Pacific Islander": "Native Hawaiian / Pac. Isl.",
         "Not Hispanic or Latino": "Not Hispanic or Latino"}
def sh(s, n=26):
    return SHORT.get(s, s)[:n]

RACE0, RACE1 = pair("races", Y0, Y1)
PSI = mantel_haenszel_or(RACE0, RACE1)
GAPS = {(v, a, b): gap_counterfactual(*pair(v, Y0, Y1), a, b)
        for v, a, b in GAP_PAIRS}

print("Generando figuras:")

# =========================================================== FIGURA 3
# (se define primero: la portada la reutiliza sin título)
# LA CURVATURA. Una función sobre un continuo -> línea. Es el mecanismo
# entero del paper en una curva, y por eso va en portada.
def fig_curv(title=True, height=3.2):
    fig, ax = plt.subplots(figsize=(6.4, height))
    xs = np.linspace(0.02, 0.985, 400)
    ys = [curvature_cost(x, PSI) * 100 for x in xs]
    ax.plot(xs * 100, ys, color=INK_2, lw=2, zorder=3)

    ors = stratum_or_ci(RACE0, RACE1)
    pts = []
    for s in ors:
        b = rate(*reversed(RACE0[s]))
        pts.append((s, b * 100, curvature_cost(b, PSI) * 100, RACE0[s][0]))
    pts.sort(key=lambda p: -p[3])

    # White y Black llevan la anotación; el resto solo el punto.
    for s, x, y, n in pts:
        big = s in ("White", "Black or African American")
        ax.scatter([x], [y], s=95 if big else 46,
                   facecolor=BLUE if big else SURFACE,
                   edgecolor=BLUE, lw=1.8, zorder=5)
    w = next(p for p in pts if p[0] == "White")
    b = next(p for p in pts if p[0] == "Black or African American")
    # Las dos etiquetas van POR DEBAJO de la curva: encima chocan con ella.
    ax.annotate(f"Black or African American\n{b[1]:.1f}% → costs {b[2]:.2f} pp",
                (b[1], b[2]), xytext=(-14, -14), textcoords="offset points",
                color=BLUE, fontsize=8.5, fontweight="bold", ha="right",
                va="top", linespacing=1.4)
    ax.annotate(f"White\n{w[1]:.1f}% → costs {w[2]:.2f} pp", (w[1], w[2]),
                xytext=(-6, -14), textcoords="offset points", color=BLUE,
                fontsize=8.5, fontweight="bold", ha="right", va="top",
                linespacing=1.4)

    # Horquilla de la diferencia mecánica, apartada a la derecha para no
    # pisar ni la curva ni los puntos.
    XB = 96.5
    for _, x, y, _ in (b, w):
        ax.plot([x, XB], [y, y], color=GRID, lw=0.9, zorder=1)
    ax.annotate("", (XB, b[2]), xytext=(XB, w[2]), textcoords="data",
                arrowprops=dict(arrowstyle="<->", color=ORANGE, lw=1.5))
    ax.annotate(f"{b[2]-w[2]:+.2f} pp\nfrom the curve\nalone",
                (XB, (w[2] + b[2]) / 2), xytext=(7, 0),
                textcoords="offset points", color=ORANGE, fontsize=8.5,
                fontweight="bold", va="center", linespacing=1.4)

    ax.set_xlim(0, 122)
    ax.set_ylim(0, 16.5)
    ax.set_xticks([0, 20, 40, 60, 80, 100])
    ax.set_xlabel(f"Approval rate in {Y0} (%)")
    ax.set_ylabel("Percentage points lost")
    clean(ax)
    if title:
        ax.set_title(f"What one group-blind odds shift costs, by starting point",
                     loc="left", fontsize=10.5, fontweight="bold", pad=9)
    fig.tight_layout()
    return fig


save(fig_curv(), "fig3_curvature")
save(fig_curv(title=False, height=3.55), "fig_cover")

# =========================================================== FIGURA 1
# Dos magnitudes en las mismas unidades sobre cuatro categorías ->
# dumbbell horizontal. Observado contra contrafactual.
def fig1():
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    labels, ys = [], []
    items = list(GAPS.items())
    for i, ((var, a, b), g) in enumerate(items):
        y = len(items) - 1 - i
        ys.append(y)
        labels.append(f"{sh(a, 24)}  vs  {sh(b, 24)}")
        o, p_ = g["observed"] * 100, g["predicted"] * 100
        ax.plot([o, p_], [y, y], color=BASELINE, lw=1.6, zorder=2,
                solid_capstyle="round")
        ax.scatter([p_], [y], s=58, facecolor=SURFACE, edgecolor=ORANGE,
                   lw=1.9, zorder=4)
        ax.scatter([o], [y], s=58, facecolor=BLUE, edgecolor=SURFACE,
                   lw=1.5, zorder=5)
        # Cuando los dos valores casi coinciden, separarlos en horizontal:
        # apilados en vertical chocan con la fila de al lado.
        near = abs(o - p_) < 0.6
        ax.annotate(f"{o:+.2f}", (o, y),
                    xytext=(14 if near else 0, 10 if near else 11),
                    textcoords="offset points", color=BLUE, fontsize=8,
                    fontweight="bold", ha="left" if near else "center")
        ax.annotate(f"{p_:+.2f}", (p_, y),
                    xytext=(-14 if near else 0, 10 if near else -17),
                    textcoords="offset points", color=ORANGE, fontsize=8,
                    fontweight="bold", ha="right" if near else "center")
    ax.axvline(0, color=BASELINE, lw=1, zorder=1)
    ax.set_yticks(ys); ax.set_yticklabels(labels, fontsize=8)
    ax.set_ylim(-0.6, len(items) - 0.4)
    ax.set_xlim(-0.3, 5.2)
    ax.set_xlabel(f"Change in the percentage-point gap, {Y0}→{Y1}")
    clean(ax, keep_left=False)
    ax.grid(axis="y", visible=False)
    ax.legend(handles=[
        plt.Line2D([], [], marker="o", ls="", markerfacecolor=BLUE,
                   markeredgecolor=SURFACE, ms=7, label="observed"),
        plt.Line2D([], [], marker="o", ls="", markerfacecolor=SURFACE,
                   markeredgecolor=ORANGE, markeredgewidth=1.9, ms=7,
                   label="what a group-blind odds shift produces")],
        loc="lower right", bbox_to_anchor=(1.01, 0.02), frameon=False,
        fontsize=8)
    ax.set_title("Every gap widened. Most of it is arithmetic.",
                 loc="left", fontsize=10.5, fontweight="bold", pad=9)
    fig.tight_layout()
    return fig


save(fig1(), "fig1_gaps")

# =========================================================== FIGURA 2
# Estimaciones con intervalo sobre categorías -> forest plot. Ordenado por
# la estimación, nunca por conveniencia: es el punto de la sección.
def fig2():
    fig, ax = plt.subplots(figsize=(6.4, 2.5))
    ors = stratum_or_ci(RACE0, RACE1)
    items = sorted(ors.items(), key=lambda kv: kv[1][0])
    ys = list(range(len(items)))[::-1]
    ax.axvline(PSI, color=ORANGE, lw=1.4, ls=(0, (4, 3)), zorder=1)
    ax.annotate(f"common shift {PSI:.3f}", (PSI, len(items) - 0.45),
                xytext=(6, 0), textcoords="offset points", color=ORANGE,
                fontsize=8, style="italic")
    for y, (s, (o, lo, hi, n)) in zip(ys, items):
        ax.plot([lo, hi], [y, y], color=BLUE, lw=2.2, zorder=3,
                solid_capstyle="round")
        ax.scatter([o], [y], s=52, facecolor=BLUE, edgecolor=SURFACE,
                   lw=1.5, zorder=4)
        ax.annotate(f"{o:.3f}", (hi, y), xytext=(8, 0),
                    textcoords="offset points", color=INK, fontsize=8,
                    va="center", fontweight="bold")
        ax.annotate(f"n = {n/1e6:.2f} M" if n >= 1e6 else f"n = {n/1e3:.0f} k",
                    (hi, y), xytext=(52, 0), textcoords="offset points",
                    color=MUTED, fontsize=7.5, va="center")
    ax.set_yticks(ys)
    ax.set_yticklabels([sh(s, 27) for s, _ in items], fontsize=8)
    ax.set_ylim(-0.6, len(items) - 0.4)
    ax.set_xlim(0.44, 0.62)
    ax.set_xlabel(f"Odds ratio, {Y0}→{Y1}   (lower = tightened more)")
    clean(ax, keep_left=False)
    ax.grid(axis="y", visible=False)
    ax.set_title("The tightening in odds is not monotone in anything",
                 loc="left", fontsize=10.5, fontweight="bold", pad=9)
    fig.tight_layout()
    return fig


save(fig2(), "fig2_forest")

# =========================================================== FIGURA 4
# Una reordenación entre dos criterios -> gráfico de pendientes. Es la
# forma que hace visible una inversión de orden.
def fig4():
    axes = []
    for var in ("sexes", "races", "ethnicities"):
        u0, u1 = pair(var, Y0, Y1)
        keep = [s for s in u0 if min(u0[s][0], u1[s][0]) >= 5000]
        k0 = {s: u0[s] for s in keep}; k1 = {s: u1[s] for s in keep}
        lg, _, _ = homogeneity_log10p(k0, k1)
        vals = [v[0] for v in stratum_or_ci(k0, k1).values()]
        axes.append((AXIS_LABELS[var], abs(lg), max(vals) / min(vals)))

    by_p = sorted(axes, key=lambda a: -a[1])
    by_m = sorted(axes, key=lambda a: -a[2])
    fig, ax = plt.subplots(figsize=(6.4, 2.6))
    for name, lg, sp in axes:
        y0 = len(axes) - by_p.index(next(a for a in by_p if a[0] == name))
        y1 = len(axes) - by_m.index(next(a for a in by_m if a[0] == name))
        colour = ORANGE if y0 != y1 else MUTED
        ax.plot([0, 1], [y0, y1], color=colour, lw=2.2, zorder=3,
                solid_capstyle="round")
        ax.scatter([0, 1], [y0, y1], s=58, facecolor=colour,
                   edgecolor=SURFACE, lw=1.5, zorder=4)
        ax.annotate(f"{name}   log$_{{10}}$p {-lg:.0f}", (0, y0),
                    xytext=(-10, 0), textcoords="offset points", ha="right",
                    va="center", color=INK, fontsize=8.5,
                    fontweight="bold" if y0 != y1 else "normal")
        ax.annotate(f"{sp:.3f}×   {name}", (1, y1), xytext=(10, 0),
                    textcoords="offset points", va="center", color=INK,
                    fontsize=8.5, fontweight="bold" if y0 != y1 else "normal")
    ax.set_xlim(-0.62, 1.62)
    ax.set_ylim(0.4, len(axes) + 0.6)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["ranked by the test\n(Breslow–Day p)",
                        "ranked by magnitude\n(odds-ratio spread)"],
                       fontsize=9)
    ax.set_yticks([])
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)
    ax.grid(visible=False)
    ax.set_title("The test and the magnitude disagree on which axis matters",
                 loc="left", fontsize=10.5, fontweight="bold", pad=9)
    fig.tight_layout()
    return fig


save(fig4(), "fig4_inversion")

print("\nListo.")
