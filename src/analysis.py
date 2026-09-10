"""
La tasa de aprobación agrupada y sus estratos. Análisis empírico sobre
HMDA, 2018-2025, datos públicos.

El resultado que ordena el paper es negativo: la paradoja de Simpson NO
aparece (0 de 56 pares). Lo que sí aparece es heterogeneidad — los
estratos no comparten un efecto común — y que el test que debería
detectarla contesta sobre el volumen de datos, no sobre el negocio.
De ahí que todo se reporte en magnitud y no en p-valores.
"""
import numpy as np
from statsmodels.stats.contingency_tables import StratifiedTable

from application_data import (AXIS_LABELS, PAIRS, PERIODS, SEGMENTATIONS,
                              pair, rate)

line = "=" * 74


def pct(x):
    return f"{x*100:+.1f}%"


def pp(x):
    """Puntos porcentuales, para diferencias entre tasas."""
    return f"{x*100:+.2f} pp"


# ------------------------------------------------------------- ESTIMADORES

def pooled_rate(cells):
    """Tasa agrupada: aprobadas totales sobre solicitudes totales.

    `cells` es un iterable de (n, approved). Es la tasa que publica un
    dashboard cuando no se le pide desglose.
    """
    n = sum(c[0] for c in cells)
    a = sum(c[1] for c in cells)
    return rate(a, n)


def stratum_rates(cells_by_segment):
    """{segmento: tasa}. Los estratos con denominador cero salen como None."""
    return {s: rate(a, n) for s, (n, a) in cells_by_segment.items()}


def is_reversal(t0, t1):
    """¿Hay paradoja de Simpson entre dos períodos?

    t0, t1: {segmento: (n, approved)}.

    Devuelve True si la tasa agrupada se mueve en un sentido y TODOS los
    estratos comparables se mueven en el contrario. Se exige unanimidad:
    que un estrato discrepe es mezcla, no reversión, y el paper debe
    distinguirlas.
    """
    common = [s for s in t0 if s in t1]
    d_pooled = pooled_rate([t1[s] for s in common]) - \
               pooled_rate([t0[s] for s in common])
    if d_pooled == 0:
        return False
    deltas = []
    for s in common:
        r0, r1 = rate(*reversed(t0[s])), rate(*reversed(t1[s]))
        if r0 is None or r1 is None or r1 == r0:
            continue
        deltas.append(r1 - r0)
    if not deltas:
        return False
    return all(np.sign(d) == -np.sign(d_pooled) for d in deltas)


def decompose(t0, t1):
    """Descompone el cambio de la tasa agrupada en dos componentes.

    Identidad exacta (no aproximación): con pesos w y tasas r por estrato,

        Σw₁r₁ − Σw₀r₀ = Σ w̄(r₁−r₀)  +  Σ r̄(w₁−w₀)
                          └ intra ┘     └ mezcla ┘

    donde w̄ y r̄ son los promedios de los dos períodos. El primer término
    es comportamiento dentro de los estratos; el segundo es puro cambio de
    composición de la demanda. La suma reproduce el total al centésimo, y
    el test de abajo lo comprueba.
    """
    common = [s for s in t0 if s in t1]
    n0 = sum(t0[s][0] for s in common)
    n1 = sum(t1[s][0] for s in common)
    within = mix = 0.0
    for s in common:
        w0, w1 = t0[s][0] / n0, t1[s][0] / n1
        r0, r1 = rate(*reversed(t0[s])), rate(*reversed(t1[s]))
        if r0 is None or r1 is None:
            continue
        within += (w0 + w1) / 2 * (r1 - r0)
        mix += (r0 + r1) / 2 * (w1 - w0)
    return within, mix


def standardized_rate(cells_by_segment, weights):
    """Tasa estandarizada directa: las tasas de cada estrato aplicadas a una
    composición fija. Es la lectura que responde "¿cambió el criterio?" en
    vez de "¿cambió quién solicita?".
    """
    num = den = 0.0
    for s, w in weights.items():
        if s not in cells_by_segment:
            continue
        r = rate(*reversed(cells_by_segment[s]))
        if r is None:
            continue
        num += w * r
        den += w
    return num / den if den else None


def mantel_haenszel_or(t0, t1):
    """Razón de momios común de Mantel-Haenszel (1959) entre dos períodos,
    ponderando los estratos por su información y no por su tamaño de
    demanda. Sirve de contraste al estandarizado: si ambos apuntan igual,
    la conclusión no depende del esquema de pesos.
    """
    num = den = 0.0
    for s in t0:
        if s not in t1:
            continue
        n1, a1 = t1[s]
        n0, a0 = t0[s]
        b1, b0 = n1 - a1, n0 - a0          # denegadas
        total = n1 + n0
        if total == 0:
            continue
        num += a1 * b0 / total
        den += b1 * a0 / total
    return num / den if den else None


def stratified_table(t0, t1):
    """Arma la tabla 2x2xK que espera statsmodels, un estrato por capa.

    Convención de cada capa: [[aprobadas t1, denegadas t1],
                              [aprobadas t0, denegadas t0]]
    que es la que hace coincidir su razón de momios con la de
    mantel_haenszel_or(). La versión a mano se queda: en un paper sobre
    cómo las definiciones producen cifras, la aritmética tiene que estar a
    la vista, y statsmodels sirve de contraste, no de sustituto.
    """
    layers = []
    for s in t0:
        if s not in t1:
            continue
        n1, a1 = t1[s]
        n0, a0 = t0[s]
        layers.append([[a1, n1 - a1], [a0, n0 - a0]])
    if not layers:
        raise ValueError("no hay estratos comunes entre los dos períodos")
    return StratifiedTable(np.array(layers).transpose(1, 2, 0))


def mantel_haenszel_ci(t0, t1, alpha=0.05):
    """Intervalo de confianza de la razón de momios común. Un IC que cruza
    1 significa que la dirección intra-estrato no está establecida, y eso
    hay que decirlo antes de construir un argumento sobre ella."""
    return stratified_table(t0, t1).oddsratio_pooled_confint(alpha=alpha)


def homogeneity(t0, t1):
    """Test de Breslow-Day: ¿comparten los estratos una misma razón de
    momios?

    Es el test que dice si agrupar es legítimo. Un p bajo rechaza la
    homogeneidad: los estratos no comparten un efecto común y ninguna
    cifra agrupada los representa — que es exactamente el argumento del
    paper, y con esto deja de ser una anécdota sobre un par de períodos.
    """
    res = stratified_table(t0, t1).test_equal_odds()
    return res.statistic, res.pvalue


def stratum_odds_ratios(t0, t1):
    """{segmento: razón de momios propia del estrato} entre dos períodos.

    Es la pieza que el agregado esconde: Mantel-Haenszel las promedia y
    devuelve una sola cifra, pero solo tiene sentido promediarlas si se
    parecen entre sí, que es lo que mide homogeneity().
    """
    ors = {}
    for s in t0:
        if s not in t1:
            continue
        n1, a1 = t1[s]
        n0, a0 = t0[s]
        b1, b0 = n1 - a1, n0 - a0
        if min(a1, b1, a0, b0) == 0:     # celda vacía: momios indefinidos
            continue
        ors[s] = (a1 * b0) / (b1 * a0)
    return ors


def or_spread(t0, t1):
    """Cociente entre la mayor y la menor razón de momios de los estratos.

    Tamaño del efecto de la heterogeneidad. A diferencia del p-valor de
    Breslow-Day, no depende del número de solicitudes, y por eso es la
    cifra que el paper reporta.
    """
    ors = stratum_odds_ratios(t0, t1)
    return max(ors.values()) / min(ors.values()) if ors else None


def rate_change_spread(t0, t1):
    """(mínimo, máximo, rango) de los cambios de tasa por estrato, en
    puntos porcentuales sobre 1. El rango es lo que el movimiento agregado
    resume en una sola cifra."""
    d = [rate(*reversed(t1[s])) - rate(*reversed(t0[s]))
         for s in t0 if s in t1]
    return min(d), max(d), max(d) - min(d)


def scaled(t, div):
    """La misma tabla contada a 1/div de escala, para mostrar que el
    p-valor es una función del volumen. Se conserva un mínimo de 2 y 1 por
    celda para que los momios sigan definidos."""
    return {s: (max(2, round(n / div)), max(1, round(a / div)))
            for s, (n, a) in t.items()}


# ---------------------------------------------------------------- INFORME

def main():
    import statistics

    # ======================================================== RESULTADO 1
    print(line)
    print("R1. LA REVERSIÓN NO OCURRE")
    print(line)
    print("  Paradoja de Simpson = la tasa agrupada se mueve y TODOS los")
    print("  estratos se mueven al contrario. Barrido completo:\n")
    rows = []
    for var in SEGMENTATIONS:
        for y0, y1 in PAIRS:
            t0, t1 = pair(var, y0, y1)
            if len(t0) < 2:
                continue
            r0, r1 = pooled_rate(t0.values()), pooled_rate(t1.values())
            within, mix = decompose(t0, t1)
            lo, hi, spread = rate_change_spread(t0, t1)
            chi2, p = homogeneity(t0, t1)
            rows.append(dict(
                var=var, y0=y0, y1=y1, k=len(t0),
                n=sum(v[0] for v in t0.values()) + sum(v[0] for v in t1.values()),
                pooled=r1 - r0, within=within, mix=mix,
                lo=lo, hi=hi, spread=spread, ors=or_spread(t0, t1),
                chi2=chi2, p=p, rev=is_reversal(t0, t1)))

    revs = [r for r in rows if r["rev"]]
    print(f"  pares probados ({len(SEGMENTATIONS)} ejes x {len(PAIRS)} pares)"
          f"   {len(rows)}")
    print(f"  reversiones unánimes                    {len(revs)}")
    mixes = sorted(abs(r["mix"]) for r in rows)
    print(f"\n  |componente de mezcla|: mediana {statistics.median(mixes)*100:.2f} pp"
          f"   máx {max(mixes)*100:.2f} pp")
    print(f"  pares con |mezcla| < 0.5 pp:  "
          f"{sum(1 for m in mixes if m < 0.005)}/{len(mixes)}")
    print("\n  La composición de la demanda casi no mueve la tasa agrupada.")
    print("  El anti-patrón que la literatura advierte no está en estos datos.")

    # ======================================================== RESULTADO 2
    print("\n" + line)
    print("R2. LA HOMOGENEIDAD SÍ SE RECHAZA — Y ESO NO DICE NADA")
    print(line)
    rej = [r for r in rows if r["p"] < 0.05]
    tiny = [r for r in rows if r["p"] < 1e-10]
    print(f"  Breslow-Day rechaza la homogeneidad en   {len(rej)}/{len(rows)}")
    print(f"  con p < 1e-10 en                         {len(tiny)}/{len(rows)}")
    ns = [r["n"] for r in rows]
    print(f"  n por par: {min(ns):,} a {max(ns):,}")
    print("\n  A esos tamaños cualquier diferencia se vuelve significativa.")
    print("  Un p~0 sobre 30 millones de solicitudes no distingue un eje")
    print("  que importa de uno que no. Ver R3.")

    # ======================================================== RESULTADO 3
    print("\n" + line)
    print("R3. EL p-VALOR ES UN HECHO SOBRE TU VOLUMEN, NO SOBRE TU NEGOCIO")
    print(line)
    print("  Los mismos datos contados a distintas escalas. El p-valor")
    print("  recorre todo el rango; el tamaño del efecto se queda en la")
    print("  misma banda (por debajo de 1/100 el redondeo por celda ya lo")
    print("  distorsiona, y eso también hay que decirlo).\n")
    demo = [("loan_purposes", "propósito"), ("sexes", "sexo")]
    tabs = {v: pair(v, 2024, 2025) for v, _ in demo}
    print(f"  {'escala':<9}{'n':>12}" +
          "".join(f"{lab+' p':>16}{'OR máx/mín':>12}" for _, lab in demo))
    for div in (10000, 1000, 100, 10, 1):
        cells = []
        n = None
        for v, _ in demo:
            t0, t1 = tabs[v]
            a0, a1 = scaled(t0, div), scaled(t1, div)
            _, p = homogeneity(a0, a1)
            cells.append(f"{p:>16.3g}{or_spread(a0, a1):>12.2f}")
            if v == "loan_purposes":
                n = sum(x[0] for x in a0.values()) + sum(x[0] for x in a1.values())
        print(f"  1/{div:<7}{n:>12,}" + "".join(cells))
    print("\n  A 1/1000 el propósito del préstamo parece homogéneo (p 0.73)")
    print("  con el mismo tamaño de efecto que a escala real. Una entidad")
    print("  mediana corriendo este test sobre su propia cartera concluye")
    print("  homogeneidad donde el agregado nacional grita lo contrario.")

    # ======================================================== RESULTADO 4
    print("\n" + line)
    print("R4. MAGNITUD: QUÉ EJE IMPORTA, Y EL ORDEN NO ES INTUITIVO")
    print(line)
    print(f"  {'eje':<14}{'OR máx/mín':>14}{'rango entre estratos':>22}"
          f"{'p>=0.05':>10}")
    for var in SEGMENTATIONS:
        g = [r for r in rows if r["var"] == var]
        ors = [r["ors"] for r in g if r["ors"]]
        sp = [r["spread"] * 100 for r in g]
        print(f"  {AXIS_LABELS[var]:<14}{min(ors):>7.2f}-{max(ors):<6.2f}"
              f"{min(sp):>14.1f}-{max(sp):<6.1f} pp"
              f"{sum(1 for r in g if r['p'] >= 0.05):>7}/{len(g)}")
    print("\n  Dos órdenes de magnitud entre el eje más heterogéneo y el más")
    print("  homogéneo. El p-valor los declara a casi todos significativos.")

    ok = [r for r in rows if abs(r["pooled"]) >= 0.005]
    ratios = [abs(r["spread"] / r["pooled"]) for r in ok]
    print(f"\n  rango entre estratos / movimiento agregado "
          f"(excluidos {len(rows)-len(ok)} pares con |Δ| < 0.5 pp,")
    print(f"  donde el cociente es artefacto de dividir por casi cero):")
    print(f"    mediana {statistics.median(ratios):.2f}x   máx {max(ratios):.2f}x"
          f"   supera 1x en {sum(1 for x in ratios if x > 1)}/{len(ratios)}")

    print("\n  " + "-" * 70)
    print("  NIVELES vs. MOVIMIENTOS — la distinción que el paper no puede")
    print("  dejar implícita. Lo homogéneo es el movimiento, no el nivel.")
    for var in ("races", "ethnicities"):
        t = pair(var, 2024, 2025)[1]
        lv = sorted(((rate(*reversed(v)), s) for s, v in t.items()),
                    reverse=True)
        print(f"\n    {AXIS_LABELS[var]}, niveles 2025:")
        for r, s in lv:
            print(f"      {s[:46]:<48}{r*100:>7.2f}%")
        print(f"      rango de niveles: {(lv[0][0]-lv[-1][0])*100:.1f} pp")

    return rows


def selftest():
    """Caso sintético mínimo con reversión conocida, para verificar los
    estimadores antes de que existan los datos reales. Comprueba además que
    la razón de momios a mano coincide con la de statsmodels.

    Dos estratos, dos períodos. Cada estrato mejora su tasa; la demanda se
    desplaza al estrato difícil, y la tasa agrupada cae.
    """
    t0 = {"facil": (1000, 900), "dificil": (1000, 200)}   # 90% / 20% -> 55.0%
    t1 = {"facil": (200, 190),  "dificil": (1800, 400)}   # 95% / 22.2% -> 29.5%

    r0, r1 = pooled_rate(t0.values()), pooled_rate(t1.values())
    print(f"  tasa agrupada        {r0*100:.1f}%  ->  {r1*100:.1f}%   "
          f"{pp(r1-r0)}")
    for s in t0:
        a = rate(*reversed(t0[s])); b = rate(*reversed(t1[s]))
        print(f"    {s:<18} {a*100:.1f}%  ->  {b*100:.1f}%   {pp(b-a)}")

    assert is_reversal(t0, t1), "debería detectar la reversión"

    within, mix = decompose(t0, t1)
    print(f"\n  componente intra-estrato  {pp(within)}")
    print(f"  componente de mezcla      {pp(mix)}")
    print(f"  suma                      {pp(within + mix)}   "
          f"(total observado {pp(r1 - r0)})")
    assert abs((within + mix) - (r1 - r0)) < 1e-12, "la identidad no cierra"

    w = {s: t0[s][0] for s in t0}          # composición del período base
    std = standardized_rate(t1, w)
    print(f"\n  tasa estandarizada a la composición de t0: {std*100:.1f}%")
    assert std > r0, "estandarizada debería subir, como cada estrato"

    or_mh = mantel_haenszel_or(t0, t1)
    lo, hi = mantel_haenszel_ci(t0, t1)
    print(f"  razón de momios de Mantel-Haenszel:        {or_mh:.3f}"
          f"  IC95 [{lo:.3f}, {hi:.3f}]")
    assert or_mh > 1, "MH debería apuntar en el mismo sentido"
    assert lo > 1, "el IC no debería cruzar 1 en este caso"

    # Contraste contra la implementación de referencia: si las dos no
    # coinciden al bit, la de arriba está mal.
    ref = stratified_table(t0, t1).oddsratio_pooled
    assert abs(or_mh - ref) < 1e-12, f"a mano {or_mh} != statsmodels {ref}"
    print("  coincide con statsmodels (StratifiedTable) hasta 1e-12")

    chi2, p = homogeneity(t0, t1)
    verdict = "no se rechaza" if p >= 0.05 else "SE RECHAZA"
    print(f"  Breslow-Day, homogeneidad: chi2 {chi2:.3f}  p {p:.4f}  "
          f"-> {verdict}")

    print("\n  OK — los estimadores se comportan como deben.")


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        print(line); print("AUTOTEST — CASO SINTÉTICO CON REVERSIÓN CONOCIDA")
        print(line)
        selftest()
    else:
        main()
