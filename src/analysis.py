"""
Reversión de la tasa de aprobación: la tasa agrupada se mueve contra la
tasa de todos sus estratos. Análisis empírico sobre datos públicos.

La maquinaria de abajo (reversión, descomposición, estandarización,
Mantel-Haenszel) ya funciona y no depende de la fuente; lo que falta es
enchufarle los datos. Ver application_data.py.
"""
import numpy as np

from application_data import PERIODS, SEGMENTATIONS, load_applications, rate

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


# ---------------------------------------------------------------- INFORME

def main():
    if not PERIODS or not SEGMENTATIONS:
        print(line)
        print("PENDIENTE: la fuente de datos no está fijada todavía.")
        print(line)
        print("  1. Decidir la fuente        -> data/README.md")
        print("  2. Fijar PERIODS y SEGMENTATIONS -> application_data.py")
        print("  3. Bajar los documentos     -> python fetch_sources.py")
        print("\nLa maquinaria de estimación ya está lista; se comprueba con")
        print("  python analysis.py --selftest")
        return

    df = load_applications()

    # ======================================================== RESULTADO 1
    print(line)
    print("R1. REVERSIÓN — TASA AGRUPADA CONTRA TASA POR ESTRATO")
    print(line)
    # TODO: tabla por segmento y período; marcar el signo de cada Δ.

    # ======================================================== RESULTADO 2
    print("\n" + line)
    print("R2. DESCOMPOSICIÓN — CUÁNTO ES MEZCLA Y CUÁNTO ES CRITERIO")
    print(line)
    # TODO: decompose() sobre la segmentación principal.

    # ======================================================== RESULTADO 3
    print("\n" + line)
    print("R3. BARRIDO — CON QUÉ FRECUENCIA REVIERTE")
    print(line)
    # TODO: is_reversal() sobre todos los pares período x segmentación.

    # ======================================================== RESULTADO 4
    print("\n" + line)
    print("R4. EL INDICADOR CORREGIDO — TRES LECTURAS DE LA MISMA TASA")
    print(line)
    # TODO: agrupada, estandarizada y MH, una al lado de la otra.
    _ = df


def selftest():
    """Caso sintético mínimo con reversión conocida, para verificar los
    estimadores antes de que existan los datos reales.

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
    print(f"  razón de momios de Mantel-Haenszel:        {or_mh:.3f}")
    assert or_mh > 1, "MH debería apuntar en el mismo sentido"

    print("\n  OK — los cuatro estimadores se comportan como deben.")


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        print(line); print("AUTOTEST — CASO SINTÉTICO CON REVERSIÓN CONOCIDA")
        print(line)
        selftest()
    else:
        main()
