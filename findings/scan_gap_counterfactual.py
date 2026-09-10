import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from analysis import mantel_haenszel_or, homogeneity, homogeneity_log10p
from application_data import pair, rate

Y0, Y1 = 2021, 2023

PAIRS = [
    ("races", "White", "Black or African American"),
    ("races", "White", "American Indian or Alaska Native"),
    ("races", "Asian", "Black or African American"),
    ("ethnicities", "Not Hispanic or Latino", "Hispanic or Latino"),
    ("sexes", "Male", "Female"),
]

print("=" * 96)
print(f"BRECHAS ENTRE PARES GRANDES, {Y0} -> {Y1}")
print("=" * 96)
print(f"  {'eje / par':<52}{'n mínimo':>11}{'brecha '+str(Y0):>11}"
      f"{'brecha '+str(Y1):>11}{'Δ':>8}")
data = {}
for var, a, b in PAIRS:
    t0, t1 = pair(var, Y0, Y1)
    if a not in t0 or b not in t0:
        print(f"  {var}: falta {a} o {b}")
        continue
    r0a, r0b = rate(*reversed(t0[a])), rate(*reversed(t0[b]))
    r1a, r1b = rate(*reversed(t1[a])), rate(*reversed(t1[b]))
    nmin = min(t0[a][0], t0[b][0], t1[a][0], t1[b][0])
    g0, g1 = (r0a - r0b) * 100, (r1a - r1b) * 100
    data[(var, a, b)] = (r0a, r0b, r1a, r1b, g0, g1, nmin)
    print(f"  {var+' · '+a[:18]+' vs '+b[:20]:<52}{nmin:>11,}"
          f"{g0:>10.2f}%{g1:>10.2f}%{g1-g0:>+8.2f}")

print("\n" + "=" * 96)
print("CONTRAFACTUAL: un solo desplazamiento en momios, ciego al grupo")
print("=" * 96)
print("  El OR común se estima sobre TODOS los estratos del eje (Mantel-")
print("  Haenszel), no sobre el par, así que no se ajusta al par que mide.\n")
print(f"  {'par':<44}{'OR común':>10}{'Δ obs.':>9}{'Δ pred.':>10}"
      f"{'residuo':>10}{'% explicado':>13}")
for (var, a, b), (r0a, r0b, r1a, r1b, g0, g1, nmin) in data.items():
    t0, t1 = pair(var, Y0, Y1)
    psi = mantel_haenszel_or(t0, t1)
    def shift(r):
        o = r / (1 - r)
        return psi * o / (1 + psi * o)
    pg1 = (shift(r0a) - shift(r0b)) * 100
    dobs, dpred = g1 - g0, pg1 - g0
    pct = dpred / dobs * 100 if dobs else float("nan")
    print(f"  {a[:16]+' vs '+b[:22]:<44}{psi:>10.3f}{dobs:>+9.2f}{dpred:>+10.2f}"
          f"{dobs-dpred:>+10.2f}{pct:>12.0f}%")

print("\n" + "=" * 96)
print("EL CONTRASTE DICE UNA COSA Y LA MAGNITUD OTRA")
print("=" * 96)
for var in ("races", "ethnicities", "sexes"):
    t0, t1 = pair(var, Y0, Y1)
    keep = [s for s in t0 if min(t0[s][0], t1[s][0]) >= 5000]
    t0k = {s: t0[s] for s in keep}; t1k = {s: t1[s] for s in keep}
    _, p = homogeneity(t0k, t1k)
    lg, chi2, df = homogeneity_log10p(t0k, t1k)
    n = sum(v[0] for v in t0k.values()) + sum(v[0] for v in t1k.values())
    ors = {s: ((t1k[s][1]*(t0k[s][0]-t0k[s][1])) /
               ((t1k[s][0]-t1k[s][1])*t0k[s][1])) for s in keep}
    print(f"\n  {var}  (n = {n:,})")
    print(f"    Breslow-Day: chi2 {chi2:.1f}, df {df}, log10 p {lg:.1f}"
          f"  -> 'NO son homogéneos'")
    print(f"    razones de momios por estrato: "
          + ", ".join(f"{s[:14]} {v:.3f}" for s, v in
                      sorted(ors.items(), key=lambda kv: -kv[1])))
    print(f"    rango: {min(ors.values()):.3f} a {max(ors.values()):.3f}"
          f"  (max/min {max(ors.values())/min(ors.values()):.3f})")
