import csv, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from analysis import pooled_rate, is_reversal, decompose, pp

MES = {m: i+1 for i, m in enumerate(
    ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"])}

def num(x):
    x = (x or "").strip().replace(",", "")
    return int(float(x)) if x else 0

CSV = ROOT / "data" / "prousuario_reclamaciones_2020-2026.csv"
with open(CSV, encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))

months, years = {}, {}
for r in rows:
    y, m = int(r["Año"]), MES[r["Mes"].strip().lower()[:3]]
    fh, fm = num(r["Favorable Hombres"]), num(r["Favorable Mujeres"])
    dh, dm = num(r["Desfavorable Hombres"]), num(r["Desfavorable Mujeres"])
    if fh + dh == 0 or fm + dm == 0:
        continue                      # un estrato vacío no es comparable
    months[(y, m)] = {"Hombres": (fh + dh, fh), "Mujeres": (fm + dm, fm)}
    a = years.setdefault(y, {"Hombres": [0, 0], "Mujeres": [0, 0]})
    a["Hombres"][0] += fh + dh; a["Hombres"][1] += fh
    a["Mujeres"][0] += fm + dm; a["Mujeres"][1] += fm
years = {y: {k: tuple(v) for k, v in d.items()} for y, d in years.items()}

def scan(tabs, label, keyfmt):
    keys = sorted(tabs)
    print(f"\n{'='*78}\n{label}  ({len(keys)} períodos, {len(keys)-1} pares)\n{'='*78}")
    hits, maj = [], 0
    for k0, k1 in zip(keys, keys[1:]):
        t0, t1 = tabs[k0], tabs[k1]
        r0, r1 = pooled_rate(t0.values()), pooled_rate(t1.values())
        d = r1 - r0
        if d == 0:
            continue
        against = [s for s in t0
                   if (t1[s][1]/t1[s][0] - t0[s][1]/t0[s][0]) * d < 0]
        n1 = sum(t1[s][0] for s in t1)
        w = sum(t1[s][0] for s in against) / n1
        if is_reversal(t0, t1):
            hits.append((k0, k1, d, decompose(t0, t1), t0, t1))
        elif w > 0.5:
            maj += 1
    print(f"  reversión unánime: {len(hits)}   mayoría del peso contra: {maj}")
    for k0, k1, d, (wi, mx), t0, t1 in hits:
        print(f"\n  *** {keyfmt(k0)} -> {keyfmt(k1)}   agrupada {pp(d)}")
        for s in t0:
            a, b = t0[s], t1[s]
            print(f"        {s:<9} {a[1]/a[0]*100:5.1f}% -> {b[1]/b[0]*100:5.1f}%"
                  f"  {pp(b[1]/b[0]-a[1]/a[0]):>10}   n {a[0]:>5,} -> {b[0]:>5,}")
        print(f"        intra {pp(wi)}   mezcla {pp(mx)}")
    return hits

print("ProUsuario / Superintendencia de Bancos RD")
print("tasa = Favorable / (Favorable + Desfavorable);  estratos = sexo")
scan(years, "PARES ANUALES", lambda k: str(k))
h = scan(months, "PARES MENSUALES CONSECUTIVOS", lambda k: f"{k[0]}-{k[1]:02d}")
