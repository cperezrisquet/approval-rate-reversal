import pathlib, statistics, sys
import numpy as np
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from analysis import (homogeneity, homogeneity_log10p, mantel_haenszel_or,
                      or_spread, pooled_rate)
from application_data import AXIS_LABELS, SEGMENTATIONS, pair, rate

Y0, Y1 = 2021, 2023

print("=" * 90)
print(f"H1 — ¿la caída en pp depende de la tasa base?  {Y0} -> {Y1}")
print("=" * 90)
pts = []
for var in SEGMENTATIONS:
    t0, t1 = pair(var, Y0, Y1)
    for s in t0:
        r0, r1 = rate(*reversed(t0[s])), rate(*reversed(t1[s]))
        if min(t0[s][0], t1[s][0]) < 5000:      # estratos ínfimos fuera
            continue
        pts.append((var, s, r0, r1, (r1 - r0) * 100, t0[s][0]))

pts.sort(key=lambda p: -p[2])
print(f"  {'eje':<14}{'estrato':<30}{'base '+str(Y0):>11}{'Δ pp':>9}{'n '+str(Y0):>12}")
for var, s, r0, r1, d, n in pts:
    print(f"  {AXIS_LABELS[var]:<14}{s[:29]:<30}{r0*100:>10.2f}%{d:>9.2f}{n:>12,}")

xs = np.array([p[2] * 100 for p in pts])
ys = np.array([p[4] for p in pts])
r = float(np.corrcoef(xs, ys)[0, 1])
slope, intercept = np.polyfit(xs, ys, 1)
print(f"\n  n estratos = {len(pts)}")
print(f"  correlación base vs Δ pp: r = {r:+.3f}")
print(f"  pendiente: {slope:+.3f} pp de caída menos por cada pp de base más")
print(f"  -> H1 {'CONFIRMADA' if r > 0.3 else 'FALSA' if r < 0.1 else 'AMBIGUA'}"
      f"  (se predijo correlación negativa entre base y CAÍDA,")
print(f"     o sea POSITIVA entre base y Δ, porque Δ es negativo)")

print("\n" + "=" * 90)
print("H2/H3 — ¿se ensancha la brecha, y lo explica un desplazamiento común?")
print("=" * 90)
print(f"  {'eje':<14}{'brecha '+str(Y0):>11}{'brecha '+str(Y1):>11}"
      f"{'Δ brecha':>10}{'OR común':>10}{'brecha pred.':>13}{'residuo':>9}"
      f"{'BD p':>10}")
rows = []
for var in SEGMENTATIONS:
    t0, t1 = pair(var, Y0, Y1)
    keep = [s for s in t0 if min(t0[s][0], t1[s][0]) >= 5000]
    if len(keep) < 2:
        continue
    t0 = {s: t0[s] for s in keep}; t1 = {s: t1[s] for s in keep}
    r0 = {s: rate(*reversed(t0[s])) for s in keep}
    r1 = {s: rate(*reversed(t1[s])) for s in keep}
    gap0 = (max(r0.values()) - min(r0.values())) * 100
    gap1 = (max(r1.values()) - min(r1.values())) * 100
    psi = mantel_haenszel_or(t0, t1)
    # Contrafactual: un solo desplazamiento en momios sobre cada base de Y0.
    pred = {}
    for s in keep:
        o = r0[s] / (1 - r0[s])
        pred[s] = psi * o / (1 + psi * o)
    gapP = (max(pred.values()) - min(pred.values())) * 100
    _, p = homogeneity(t0, t1)
    rows.append((var, gap0, gap1, gap1 - gap0, psi, gapP, gap1 - gapP, p))
    print(f"  {AXIS_LABELS[var]:<14}{gap0:>10.2f}%{gap1:>10.2f}%{gap1-gap0:>+9.2f}"
          f"{psi:>10.3f}{gapP:>12.2f}%{gap1-gapP:>+9.2f}{p:>10.2g}")

print("\n  'brecha pred.' = la que produciría aplicar el OR común a las bases")
print("  de 2021. 'residuo' = observada menos predicha: lo que NO explica un")
print("  desplazamiento uniforme en momios.")
wid = [x for x in rows if x[3] > 0]
print(f"\n  ejes donde la brecha en pp SE ENSANCHA: {len(wid)}/{len(rows)}")
res = [abs(x[6]) for x in rows]
print(f"  |residuo|: mediana {statistics.median(res):.2f} pp   máx {max(res):.2f} pp")
