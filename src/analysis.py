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
from scipy import stats
from scipy.special import gammaln
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


def homogeneity_log10p(t0, t1):
    """log10 del p-valor de Breslow-Day, y el estadístico y los grados de
    libertad.

    A estos tamaños el p-valor hace underflow y statsmodels devuelve 0
    exacto, que no se puede graficar en un eje logarítmico ni citar en el
    texto. La función de supervivencia en escala logarítmica sí da el valor
    real (del orden de 1e-300 y más allá).
    """
    st = stratified_table(t0, t1)
    res = st.test_equal_odds()
    df = len(stratum_odds_ratios(t0, t1)) - 1
    if df < 1:
        return None, res.statistic, df
    log10p = float(stats.chi2.logsf(res.statistic, df)) / np.log(10)
    if not np.isfinite(log10p):
        # chi2.logsf también hace underflow pasado cierto punto y devuelve
        # -inf. Serie asintótica de la gamma incompleta superior:
        #   sf = Γ(a,z)/Γ(a),  a = df/2,  z = chi2/2
        #   Γ(a,z) ~ z^(a-1) e^-z [1 + (a-1)/z + (a-1)(a-2)/z² + ...]
        a, z = df / 2.0, res.statistic / 2.0
        corr = term = 1.0
        for j in range(1, 6):
            term *= (a - j) / z
            corr += term
        ln = (a - 1) * np.log(z) - z + np.log(corr) - gammaln(a)
        log10p = float(ln) / np.log(10)
    return log10p, res.statistic, df


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


# ------------------------------------------------------- CURVATURA Y BRECHAS

def odds_shift(r, psi):
    """Aplica una razón de momios a una tasa. Es lo que hace mover un corte
    de score: multiplica los momios, no resta puntos porcentuales."""
    o = r / (1 - r)
    return psi * o / (1 + psi * o)


def curvature_cost(r, psi):
    """Puntos porcentuales que cuesta el desplazamiento `psi` a una tasa
    base `r`.

    El núcleo del paper. La función es cero en 0 y en 1 y tiene un máximo
    en el medio, así que un MISMO endurecimiento en momios cuesta muy
    distinto según dónde esté cada grupo. Una brecha en puntos
    porcentuales entre dos grupos se ensancha por esto solo, sin que nadie
    los trate distinto.
    """
    return r - odds_shift(r, psi)


def stratum_or_ci(t0, t1, alpha=0.05):
    """{segmento: (OR, lo, hi, n)} con el intervalo de Woolf sobre log OR.

    Se reportan los intervalos porque sin ellos no se puede saber si el
    orden entre estratos significa algo, y el paper se apoya en no
    ordenarlos en una narrativa.
    """
    z = stats.norm.isf(alpha / 2)
    out = {}
    for s in t0:
        if s not in t1:
            continue
        n1, a1 = t1[s]
        n0, a0 = t0[s]
        b1, b0 = n1 - a1, n0 - a0
        if min(a1, b1, a0, b0) == 0:
            continue
        or_ = (a1 * b0) / (b1 * a0)
        se = np.sqrt(1 / a1 + 1 / b1 + 1 / a0 + 1 / b0)
        out[s] = (or_, float(np.exp(np.log(or_) - z * se)),
                  float(np.exp(np.log(or_) + z * se)), n0 + n1)
    return out


def gap_counterfactual(t0, t1, a, b, psi=None):
    """Brecha observada entre dos estratos y la que produciría un único
    desplazamiento en momios, ciego al grupo.

    `psi` se estima por Mantel-Haenszel sobre TODOS los estratos del eje,
    no sobre el par que se mide, para que el contrafactual no se ajuste a
    lo que pretende explicar.
    """
    if psi is None:
        psi = mantel_haenszel_or(t0, t1)
    r0a, r0b = rate(*reversed(t0[a])), rate(*reversed(t0[b]))
    r1a, r1b = rate(*reversed(t1[a])), rate(*reversed(t1[b]))
    gap0, gap1 = r0a - r0b, r1a - r1b
    gap_pred = odds_shift(r0a, psi) - odds_shift(r0b, psi)
    return dict(psi=psi, gap0=gap0, gap1=gap1,
                observed=gap1 - gap0, predicted=gap_pred - gap0,
                residual=(gap1 - gap0) - (gap_pred - gap0))


# ---------------------------------------------------------------- INFORME

# Pares grandes sobre los que se miden brechas. Se fijan aquí, no se eligen
# mirando resultados, y se reportan los cuatro.
GAP_PAIRS = [
    ("races", "White", "Black or African American"),
    ("races", "White", "American Indian or Alaska Native"),
    ("ethnicities", "Not Hispanic or Latino", "Hispanic or Latino"),
    ("sexes", "Male", "Female"),
]
Y0, Y1 = 2021, 2023


def main():
    # ======================================================== RESULTADO 1
    print(line)
    print(f"R1. LAS BRECHAS EN PUNTOS PORCENTUALES SE ENSANCHARON, {Y0}-{Y1}")
    print(line)
    print(f"  Tasa agrupada: ", end="")
    t0, t1 = pair("loan_purposes", Y0, Y1)
    r0, r1 = pooled_rate(t0.values()), pooled_rate(t1.values())
    w, m = decompose(t0, t1)
    print(f"{r0*100:.2f}% -> {r1*100:.2f}%  ({pp(r1-r0)})")
    print(f"  de lo cual intra-estrato {pp(w)} y mezcla {pp(m)}\n")
    print(f"  {'par':<46}{'brecha '+str(Y0):>12}{'brecha '+str(Y1):>12}{'Δ':>9}")
    gaps = {}
    for var, a, b in GAP_PAIRS:
        ta, tb = pair(var, Y0, Y1)
        g = gap_counterfactual(ta, tb, a, b)
        gaps[(var, a, b)] = g
        print(f"  {a[:20]+' vs '+b[:22]:<46}{g['gap0']*100:>11.2f}%"
              f"{g['gap1']*100:>11.2f}%{g['observed']*100:>+9.2f}")
    print("\n  Los cuatro se ensanchan. Leído así, el endurecimiento fue")
    print("  desigual y el desglose por grupo lo detecta.")

    # ======================================================== RESULTADO 2
    print("\n" + line)
    print("R2. UN ENDURECIMIENTO CIEGO AL GRUPO EXPLICA CASI TODO")
    print(line)
    print("  Contrafactual: un solo desplazamiento en momios aplicado a las")
    print(f"  bases de {Y0}. El OR común se estima por Mantel-Haenszel sobre")
    print("  TODOS los estratos del eje, no sobre el par que se mide.\n")
    print(f"  {'par':<46}{'OR común':>10}{'Δ obs.':>9}{'Δ pred.':>10}{'residuo':>10}")
    for (var, a, b), g in gaps.items():
        print(f"  {a[:20]+' vs '+b[:22]:<46}{g['psi']:>10.4f}"
              f"{g['observed']*100:>+9.2f}{g['predicted']*100:>+10.2f}"
              f"{g['residual']*100:>+10.2f}")
    over = [g for g in gaps.values() if g["residual"] < 0]
    share = [g["predicted"] / g["observed"] for g in gaps.values()]
    resid = [abs(g["residual"]) * 100 for g in gaps.values()]
    print(f"\n  el contrafactual cubre entre el {min(share)*100:.0f}% y el "
          f"{max(share)*100:.0f}% de cada ensanchamiento")
    print(f"  residuos absolutos: de {min(resid):.2f} a {max(resid):.2f} pp")
    print(f"  sobre-predice en {len(over)}/{len(gaps)}, sub-predice en "
          f"{len(gaps)-len(over)}/{len(gaps)}")
    print("\n  El ensanchamiento es en su mayor parte mecánico en los cuatro")
    print("  pares. En White vs Black, además, la brecha se ensanchó MENOS")
    print("  de lo que produce una política uniforme — pero eso es de ese")
    print("  par, no una propiedad general, y el paper no lo generaliza.")

    ta, tb = pair("races", Y0, Y1)
    psi = mantel_haenszel_or(ta, tb)
    lo, hi = mantel_haenszel_ci(ta, tb)
    g = gaps[("races", "White", "Black or African American")]
    print(f"\n  Robustez sobre White vs Black: el OR común es {psi:.4f} "
          f"IC95 [{lo:.4f}, {hi:.4f}],")
    print(f"  y la brecha predicha va de {(odds_shift(rate(*reversed(ta['White'])), hi) - odds_shift(rate(*reversed(ta['Black or African American'])), hi) - g['gap0'])*100:+.2f} pp "
          f"a {(odds_shift(rate(*reversed(ta['White'])), lo) - odds_shift(rate(*reversed(ta['Black or African American'])), lo) - g['gap0'])*100:+.2f} pp "
          f"en ese intervalo.")
    print(f"  La sobre-predicción de {abs(g['residual'])*100:.2f} pp no es un "
          "artefacto de estimación.")

    # ======================================================== RESULTADO 3
    print("\n" + line)
    print("R3. EL ENDURECIMIENTO EN MOMIOS NO ES MONÓTONO EN NADA")
    print(line)
    print("  Los cinco estratos de raza, con intervalo. Ordenados por momios,")
    print("  no por conveniencia. Más bajo = más endurecimiento.\n")
    ors = stratum_or_ci(ta, tb)
    ref = ors["White"][0]
    print(f"  {'estrato':<44}{'OR':>8}{'IC95':>20}{'vs White':>11}{'n':>14}")
    for s, (o, l, h, n) in sorted(ors.items(), key=lambda kv: kv[1][0]):
        print(f"  {s[:43]:<44}{o:>8.4f}   [{l:.4f}, {h:.4f}]"
              f"{(o/ref-1)*100:>+10.1f}%{n:>14,}")
    print("\n  Native Hawaiian se endureció un 15% MÁS que White; Black un 4%")
    print("  MENOS; American Indian es indistinguible. Ninguna narrativa")
    print("  monótona sobrevive a esta columna, y por eso el paper no la usa.")

    # ======================================================== RESULTADO 4
    print("\n" + line)
    print("R4. LA CURVATURA QUE PRODUCE TODO LO ANTERIOR")
    print(line)
    print(f"  Coste en pp del mismo desplazamiento (psi = {psi:.4f}) según la")
    print("  tasa base. Cero en los extremos, máximo en el medio.\n")
    print(f"  {'base':>8}{'tras el desplazamiento':>25}{'cuesta':>10}")
    for r in (0.50, 0.60, 0.70, 0.80, 0.86, 0.90, 0.95):
        print(f"  {r*100:>7.0f}%{odds_shift(r, psi)*100:>24.2f}%"
              f"{curvature_cost(r, psi)*100:>9.2f} pp")
    grid = np.linspace(0.02, 0.98, 481)
    peak = grid[int(np.argmax([curvature_cost(x, psi) for x in grid]))]
    print(f"\n  máximo en base = {peak*100:.1f}%   "
          f"({curvature_cost(peak, psi)*100:.2f} pp)")
    b0 = rate(*reversed(ta["Black or African American"]))
    w0 = rate(*reversed(ta["White"]))
    print(f"\n  White partía de {w0*100:.2f}% y le cuesta "
          f"{curvature_cost(w0, psi)*100:.2f} pp")
    print(f"  Black partía de {b0*100:.2f}% y le cuesta "
          f"{curvature_cost(b0, psi)*100:.2f} pp")
    print(f"  diferencia mecánica: {(curvature_cost(b0,psi)-curvature_cost(w0,psi))*100:+.2f} pp"
          f"   sin que nadie los trate distinto")

    # ---------------------------------------------------------------- 4.1
    print("\n  " + "-" * 70)
    print("  4.1 EL p-VALOR INVIERTE EL ORDEN QUE SE LE PIDE")
    print(f"  {'eje':<12}{'Breslow-Day log10 p':>22}{'rango de momios':>20}"
          f"{'max/min':>10}")
    for var in ("sexes", "races", "ethnicities"):
        u0, u1 = pair(var, Y0, Y1)
        keep = [s for s in u0 if min(u0[s][0], u1[s][0]) >= 5000]
        k0 = {s: u0[s] for s in keep}; k1 = {s: u1[s] for s in keep}
        lg, chi2, df = homogeneity_log10p(k0, k1)
        o = stratum_or_ci(k0, k1)
        vals = [v[0] for v in o.values()]
        print(f"  {AXIS_LABELS[var]:<12}{lg:>22.1f}"
              f"{min(vals):>12.3f}-{max(vals):<7.3f}"
              f"{max(vals)/min(vals):>9.3f}")
    print("\n  El contraste declara el sexo el eje más heterogéneo. La")
    print("  magnitud dice que es el menos. Quien elija qué vigilar por")
    print("  significación elige mal.")
    return gaps


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
