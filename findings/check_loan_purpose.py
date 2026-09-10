import json, sys
sys.path.insert(0, "/Users/cperez/PycharmProjects/cifras-correctas/approval-rate-reversal/src")
from analysis import (pooled_rate, is_reversal, decompose, standardized_rate,
                      mantel_haenszel_or, mantel_haenszel_ci, homogeneity, pp)

LP = {"1": "Compra", "2": "Mejora", "31": "Refinanciación",
      "32": "Cash-out refi", "4": "Otro", "5": "No aplica"}

def table(year):
    """{segmento: (n, aprobadas)}  con  n = a1+a2+a3,  aprobadas = a1+a2."""
    d = json.load(open(f"hmda_{year}.json"))
    cells = {}
    for a in d["aggregations"]:
        cells.setdefault(a["loan_purposes"], {})[a["actions_taken"]] = a["count"]
    out = {}
    for lp, acts in cells.items():
        a1, a2, a3 = acts.get("1", 0), acts.get("2", 0), acts.get("3", 0)
        out[LP.get(lp, lp)] = (a1 + a2 + a3, a1 + a2)
    return out

t0, t1 = table(2024), table(2025)

print("=" * 74)
print("HMDA 2024 -> 2025, 51 jurisdicciones, tasa = (1+2)/(1+2+3)")
print("=" * 74)
r0, r1 = pooled_rate(t0.values()), pooled_rate(t1.values())
n0 = sum(v[0] for v in t0.values()); n1 = sum(v[0] for v in t1.values())
print(f"\n  TASA AGRUPADA   {r0*100:.2f}%  ->  {r1*100:.2f}%   {pp(r1-r0)}")
print(f"  solicitudes     {n0:,}  ->  {n1:,}")

print(f"\n  {'Segmento':<16}{'n 2024':>11}{'n 2025':>11}"
      f"{'tasa 24':>10}{'tasa 25':>10}{'Δ':>11}{'peso 24':>9}{'peso 25':>9}")
for s in sorted(t0, key=lambda k: -t0[k][0]):
    a, b = t0[s], t1[s]
    ra, rb = a[1]/a[0], b[1]/b[0]
    print(f"  {s:<16}{a[0]:>11,}{b[0]:>11,}{ra*100:>9.2f}%{rb*100:>9.2f}%"
          f"{pp(rb-ra):>11}{a[0]/n0*100:>8.1f}%{b[0]/n1*100:>8.1f}%")

print(f"\n  ¿REVIERTE (unanimidad)?  {is_reversal(t0, t1)}")

up = [s for s in t0 if t1[s][1]/t1[s][0] > t0[s][1]/t0[s][0]]
print(f"  segmentos que suben: {len(up)}/{len(t0)}  {sorted(up)}")

w, m = decompose(t0, t1)
print(f"\n  componente intra-estrato  {pp(w)}")
print(f"  componente de mezcla      {pp(m)}")
print(f"  suma                      {pp(w+m)}   (observado {pp(r1-r0)})")

std = standardized_rate(t1, {s: t0[s][0] for s in t0})
print(f"\n  estandarizada a composición 2024: {std*100:.2f}%  "
      f"(agrupada 2024 {r0*100:.2f}%)  {pp(std-r0)}")
orm = mantel_haenszel_or(t0, t1); lo, hi = mantel_haenszel_ci(t0, t1)
print(f"  razón de momios MH:  {orm:.4f}  IC95 [{lo:.4f}, {hi:.4f}]")
chi2, p = homogeneity(t0, t1)
print(f"  Breslow-Day: chi2 {chi2:.1f}  p {p:.3g}")
