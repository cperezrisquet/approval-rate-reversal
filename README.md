# Widening by Curvature

What a percentage-point gap between groups measures. HMDA, 2021–2023.

Entry #2 in the series *Cifras correctas, conclusiones falsas* — analytical
anti-patterns in banking and fintech measurement, each entry self-contained.
Entry #1: [Same System, Opposite
Trends](https://github.com/cperezrisquet/active-user-divergence).

**Paper:** [`paper/Widening-by-Curvature.pdf`](paper/Widening-by-Curvature.pdf)
— 9 pages.

## The claim

Lenders do not tighten by subtracting percentage points. They move a score
cutoff or a debt-to-income ceiling, which is a multiplicative shift in odds.
A multiplicative shift costs a different number of percentage points depending
on where each group started, because the cost function
*r*(1−*r*)(1−ψ)/(1−*r*+ψ*r*) is zero at both ends and maximal in the middle.
So a gap measured in percentage points widens when a single group-blind
tightening is applied to groups that start from different places.

Measured on the 2021–2023 mortgage contraction, that arithmetic accounts for
most of the widening observed on every axis. The paper argues the
percentage-point gap is the wrong instrument, and states explicitly that
neither the widening nor its arithmetic explanation licenses a conclusion
about differential treatment, in either direction.

## Headline findings

Every row is reproducible from this repository.

| Finding | Result |
|---|---|
| Pooled approval rate, 2021 → 2023 | 84.30 % → 74.92 % (**−9.38 pp**) |
| of which within-stratum / composition | −7.61 pp / −1.77 pp |
| Gap widening, White vs Black | **+3.26 pp** (12.33 → 15.58) |
| Same, under one group-blind odds shift | **+4.15 pp** — it *over*-predicts |
| Share of each widening the blind shift reproduces | **46 % to 128 %**, residuals 0.09–0.90 pp |
| Odds ratio, Black / White | 0.5755 / 0.5536 — Black tightened **4.0 % less** |
| Odds ratio, Native Hawaiian / Pac. Isl. | 0.4702 — tightened **15.1 % more** |
| Peak of the curvature cost | baseline **57.2 %**, at 14.58 pp |
| Breslow–Day ranking vs. magnitude ranking | inverted: sex log₁₀p −370.9 / 1.115×, race −48.8 / **1.224×** |

The pre-registered hypothesis was **false**. It predicted the
percentage-point loss would be largest where baselines were lowest; pooled
across 28 strata the correlation is r = −0.025, and the test design was wrong
too. Government-backed programmes barely tightened (VA −2.51 pp, FHA −3.66)
while conventional lending took −10.66. Both the pre-registration and the
failure are in [`findings/`](findings/), committed before the results.

### What this repository does not claim

The heterogeneity results concern how a gap **moves** when a system tightens.
They say nothing about the **level** of any gap — the 12.33 pp White–Black gap
that already existed in 2021 is not explained by curvature and is not analysed
here — and nothing about causes. There are no applicant-level controls for
income, collateral, debt burden or credit history: the aggregations endpoint
does not expose them and HMDA does not publish credit scores at all.

Section 7 of the paper states the two inferences it does not license, and they
should travel together whenever any of this is quoted.

## Reproducing

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cd src
python analysis.py --selftest   # verifies the estimators on a synthetic case
python fetch_sources.py         # refreshes the API responses (already committed)
python analysis.py              # results 1-4, printed to stdout
python figures.py               # regenerates figures/ as SVG + PNG
python figura_post_es.py        # the square figure for the Spanish post
python build_paper.py           # assembles paper/paper.html
```

To rebuild the PDF from the assembled HTML:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf=paper/Widening-by-Curvature.pdf \
  file://$PWD/paper/paper.html
```

`build_paper.py` counts any `[TODO]` markers left in the document and warns.

## The estimators

All in [`src/analysis.py`](src/analysis.py), all independent of the source.

| Function | What it answers |
|---|---|
| `odds_shift` / `curvature_cost` | what a multiplicative tightening does to a rate, and what it costs in percentage points from a given starting point |
| `gap_counterfactual` | the observed change in a gap beside the change one group-blind odds shift produces. ψ comes from Mantel–Haenszel across *all* strata of the axis, never the pair, so it cannot be fitted to the gap it explains |
| `stratum_or_ci` | per-stratum odds ratios with Woolf intervals — without them there is no way to know whether an ordering means anything |
| `mantel_haenszel_or` / `_ci` | the common shift and its interval |
| `homogeneity` / `homogeneity_log10p` | Breslow–Day, and the same p-value in log space. Past ~10⁻³⁰⁸ the float underflows and `scipy` returns 0; the fallback is the asymptotic expansion of the upper incomplete gamma, checked against `scipy` where `scipy` still works |
| `decompose` | within-stratum against composition, an exact identity |
| `is_reversal` / `or_spread` / `scaled` | from the earlier line of work; see `findings/` |

`python analysis.py --selftest` runs them against a synthetic case with a
known reversal, asserts the decomposition identity closes, and checks the
hand-written Mantel–Haenszel estimator against `statsmodels` to 1e-12.

## Data

Public, no key, no registration. **FFIEC**, *HMDA Data Browser*, filing years
2018–2025, 50 states + DC, retrieved 10 September 2026. Field definitions and
the `action_taken` construction are in [`data/README.md`](data/README.md).

The 64 API responses behind the analysis are committed — they are public
aggregate counts of roughly 500 bytes each — so every number can be rechecked
without contacting the API.

## Layout

```
src/      application_data.py  the HMDA source, schema and rate definition
          analysis.py          estimators + results 1-4
          figures.py           the paper's figures
          figura_post_es.py    the square figure for the Spanish post
          build_paper.py       assembles HTML from template + SVGs
          fetch_sources.py     refreshes the API responses
paper/    template, assembled HTML, PDF
figures/  SVG (vector, used in the paper) and PNG
data/     hmda_aggregations/ — the 64 committed API responses
findings/ pre-registrations, results, and the record of what failed
```

## License

Code under MIT. The paper text is the author's. HMDA data remains subject to
its publisher's terms; filings are subject to revision.
