import json, pathlib, sys, time, urllib.parse
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))
from analysis import pooled_rate, is_reversal, decompose, pp
from fetch_sources import get   # contexto TLS + reintento por curl

B = "https://ffiec.cfpb.gov/v2/data-browser-api/view/aggregations"
ST = ("AL,AK,AZ,AR,CA,CO,CT,DE,DC,FL,GA,HI,ID,IL,IN,IA,KS,KY,LA,ME,MD,MA,MI,"
      "MN,MS,MO,MT,NE,NV,NH,NJ,NM,NY,NC,ND,OH,OK,OR,PA,RI,SC,SD,TN,TX,UT,VT,"
      "VA,WA,WV,WI,WY")
YEARS = list(range(2018, 2026))

VARS = {
    "loan_purposes":        "1,2,31,32,4,5",
    "loan_types":           "1,2,3,4",
    "lien_statuses":        "1,2",
    "construction_methods": "1,2",
    "total_units":          "1,2,3,4",
    "races":                ("American Indian or Alaska Native,Asian,"
                             "Black or African American,"
                             "Native Hawaiian or Other Pacific Islander,White"),
    "sexes":                "Male,Female,Joint",
    "ethnicities":          "Hispanic or Latino,Not Hispanic or Latino,Joint",
}
CACHE = (pathlib.Path(__file__).resolve().parent.parent
         / "data" / "hmda_aggregations")
CACHE.mkdir(parents=True, exist_ok=True)


def fetch(var, vals, year):
    f = CACHE / f"{var}_{year}.json"
    if f.exists():
        return json.loads(f.read_text())
    q = urllib.parse.urlencode({"years": year, "states": ST,
                                "actions_taken": "1,2,3", var: vals})
    for attempt in range(5):
        try:
            d = json.loads(get(f"{B}?{q}", timeout=120))
            break
        except Exception as exc:                       # noqa: BLE001
            wait = 3 * 2 ** attempt
            print(f"    {var} {year}: {exc} — reintento en {wait}s", flush=True)
            time.sleep(wait)
    else:
        raise RuntimeError(f"{var} {year}: agotados los reintentos")
    f.write_text(json.dumps(d))
    time.sleep(0.3)
    return d


def table(var, vals, year):
    """{segmento: (n, aprobadas)} con n = a1+a2+a3, aprobadas = a1+a2."""
    cells = {}
    for a in fetch(var, vals, year)["aggregations"]:
        key = a.get(var)
        if key is None:
            continue
        cells.setdefault(str(key), {})[a["actions_taken"]] = a["count"]
    out = {}
    for k, acts in cells.items():
        a1, a2, a3 = acts.get("1", 0), acts.get("2", 0), acts.get("3", 0)
        if a1 + a2 + a3 > 0:
            out[k] = (a1 + a2 + a3, a1 + a2)
    return out


rows = []
for var, vals in VARS.items():
    print(f"bajando {var} ...", flush=True)
    tabs = {y: table(var, vals, y) for y in YEARS}
    for y0, y1 in zip(YEARS, YEARS[1:]):
        t0, t1 = tabs[y0], tabs[y1]
        common = [s for s in t0 if s in t1]
        if len(common) < 2:
            continue
        t0 = {s: t0[s] for s in common}; t1 = {s: t1[s] for s in common}
        r0, r1 = pooled_rate(t0.values()), pooled_rate(t1.values())
        d = r1 - r0
        against = [s for s in common
                   if (t1[s][1]/t1[s][0] - t0[s][1]/t0[s][0]) * d < 0]
        n1 = sum(t1[s][0] for s in common)
        wagainst = sum(t1[s][0] for s in against) / n1
        w, m = decompose(t0, t1)
        rows.append(dict(var=var, pair=f"{y0}->{y1}", d=d, k=len(common),
                         against=len(against), wagainst=wagainst,
                         full=is_reversal(t0, t1), within=w, mix=m))

print("\n" + "=" * 96)
print("BARRIDO COMPLETO — distribución, no máximo")
print("=" * 96)
print(f"{'segmentación':<22}{'par':<13}{'Δ agrup':>9}{'estratos':>9}"
      f"{'contra':>7}{'peso contra':>12}{'intra':>9}{'mezcla':>9}{'REV':>6}")
for r in rows:
    print(f"{r['var']:<22}{r['pair']:<13}{r['d']*100:>+8.2f} {r['k']:>8}"
          f"{r['against']:>7}{r['wagainst']*100:>11.1f}%"
          f"{r['within']*100:>+8.2f} {r['mix']*100:>+8.2f} "
          f"{'SI' if r['full'] else '·':>5}")

full = [r for r in rows if r["full"]]
maj = [r for r in rows if not r["full"] and r["wagainst"] > 0.5]
any_ = [r for r in rows if r["against"] > 0]
print(f"\n  pares probados                         {len(rows)}")
print(f"  reversión unánime (paradoja de Simpson) {len(full)}")
print(f"  mayoría del peso contra el agregado     {len(maj)}")
print(f"  al menos un estrato contra el agregado  {len(any_)}")
if full:
    print("\n  UNÁNIMES:")
    for r in full:
        print(f"    {r['var']} {r['pair']}: agrupada {pp(r['d'])}, "
              f"intra {pp(r['within'])}, mezcla {pp(r['mix'])}")
json.dump(rows, open("scan_rows.json", "w"), indent=1)
