# Significant by Volume

What a homogeneity test on approval rates measures. HMDA, 2018–2025.

Entry #2 in the series *Cifras correctas, conclusiones falsas* — analytical
anti-patterns in banking and fintech measurement, each entry self-contained.
Entry #1: [Same System, Opposite
Trends](https://github.com/cperezrisquet/active-user-divergence).

**Paper:** [`paper/Significant-by-Volume.pdf`](paper/Significant-by-Volume.pdf)
— 9 pages.

## The claim

The standard warning against aggregate approval rates invokes Simpson's
paradox. Across 56 tests on public mortgage-application data that paradox
never occurs. The pooled rate is still a poor summary of its strata — the
strata do not share a common effect — but the test that establishes this
mostly reports how many applications were counted. Reported as magnitude
instead, the eight candidate segmentation axes differ by more than an order
of magnitude in heterogeneity, and the ranking is not the intuitive one.

## Headline findings

Every row is reproducible from this repository.

| Finding | Result |
|---|---|
| Simpson reversals across 8 axes × 7 year-pairs | **0 of 56** |
| Pairs where the composition term is under 0.5 pp | **49 of 56** (median 0.07 pp) |
| Pairs where Breslow–Day rejects a common odds ratio | **53 of 56** (47 at p < 10⁻¹⁰) |
| Loan purpose, 2024→2025, at full scale | χ² = 1855.9, df 5, **p ≈ 10⁻³⁹⁹** |
| The same data at 1/1000 scale | **p = 0.73** — effect size unchanged |
| Heterogeneity, widest axis (loan purpose) | **2.19×** |
| Heterogeneity, narrowest axes (sex, ethnicity) | **1.08× / 1.09×** |
| Spread between strata vs. the pooled movement | median **0.65×**, exceeds it in 17 of 48 |

The pre-registered hypothesis was **false**: the composition term for
2024→2025 by loan purpose is −0.07 pp against a within-stratum term of
+1.74 pp. The record is in [`findings/`](findings/).

### On the demographic axes

The heterogeneity result concerns year-over-year **movements**, not levels.
Levels differ substantially — 15.1 pp across reported race in 2025, 9.2 pp
across ethnicity — and nothing in this paper speaks to their causes. What is
nearly homogeneous is the year-over-year change. Section 6.1 of the paper
states the distinction; it should not be dropped when the result is quoted.

## What was decided, and why

1. **The source is HMDA**, through the FFIEC Data Browser's
   `view/aggregations` endpoint. There is no public Dominican source for
   credit approval rates — the BCRD publishes payments, not applications, and
   the Superintendencia de Bancos publishes complaints and sanctions. The one
   Dominican source with the right shape (ProUsuario favourable-decision
   rates) carries a single segmentation axis and shows no reversal either;
   both checks are recorded in [`findings/`](findings/).
2. **The aggregations endpoint replaces the loan-level download.** It returns
   the cross-tabulation in ~500 bytes, so the 64 responses behind this paper
   are committed and the analysis is recheckable without contacting the API.
3. **The thesis followed the data, not the title.** The repository name still
   says `approval-rate-reversal`, which is what was expected; the reversal is
   the negative result.

## Data sources

All public. No proprietary or institution-internal data is used at any stage,
and none is required to reproduce any figure. Field definitions and the
`action_taken` construction are documented in
[`data/README.md`](data/README.md).

- **FFIEC**, *HMDA Data Browser*, filing years 2018–2025, 50 states + DC.
  Retrieved 10 September 2026.
- **Superintendencia de Bancos de la República Dominicana**, *Estadísticas de
  ProUsuario, 2020–2026* — used only for the Dominican cross-check.

## Reproducing

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cd src
python analysis.py --selftest   # verifies the estimators on a synthetic case
python fetch_sources.py         # refreshes the API responses (already committed)
python analysis.py              # results 1-4, printed to stdout
python figures.py               # regenerates figures/ as SVG + PNG
python build_paper.py           # assembles paper/paper.html
```

To rebuild the PDF from the assembled HTML:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf=paper/Significant-by-Volume.pdf \
  file://$PWD/paper/paper.html
```

`build_paper.py` counts the `[TODO]` markers left in the document and warns.
Do not print the PDF while any remain.

## The estimators

Four readings of the same application file, all in
[`src/analysis.py`](src/analysis.py) and all independent of the source:

| Function | What it answers |
|---|---|
| `pooled_rate` | the rate a dashboard shows when nobody asks for a breakdown |
| `is_reversal` | whether the pooled rate moves against *every* stratum — unanimity is required, so that ordinary mix effects are not reported as paradoxes |
| `decompose` | how much of the pooled change is within-segment behaviour and how much is composition; an exact identity, not an approximation |
| `standardized_rate` | the rate under a fixed composition — the reading that answers "did the criterion change?" rather than "did the applicants change?" |
| `mantel_haenszel_or` / `mantel_haenszel_ci` | the same comparison weighted by information instead of demand, with a confidence interval; if it agrees with the standardised rate, the conclusion does not depend on the weighting scheme |
| `homogeneity` | Breslow–Day test — whether the strata share a common odds ratio at all. Section 5 of the paper is about why its answer cannot be taken at face value. |
| `homogeneity_log10p` | the same p-value in log space. Past roughly 10⁻³⁰⁸ the float underflows and `scipy` returns 0; this falls back to the asymptotic expansion of the upper incomplete gamma, checked against `scipy` where `scipy` still works. |
| `or_spread` / `rate_change_spread` | the volume-free effect sizes the paper reports instead of the p-value |
| `scaled` | the same table counted at 1/n of scale, for the demonstration in section 5 |

`python analysis.py --selftest` runs them against a synthetic two-stratum case
with a known reversal, asserts that the decomposition identity closes, and
checks the hand-written Mantel–Haenszel estimator against
`statsmodels.stats.contingency_tables.StratifiedTable` to 1e-12. The
hand-written version stays: in a paper about how definitions produce figures,
the arithmetic has to be on the page, and statsmodels is the check on it.

## Layout

```
src/      application_data.py  the HMDA source, schema and rate definition
          analysis.py          estimators + results 1-4
          figures.py           figure generation
          build_paper.py       assembles HTML from template + SVGs
          fetch_sources.py     refreshes the API responses
paper/    template, assembled HTML, PDF
figures/  SVG (vector, used in the paper) and PNG
data/     hmda_aggregations/ — the 64 committed API responses
findings/ the pre-registered hypothesis and the negative results
```

## License

Code under MIT. The paper text is the author's. Source data remains subject to
its publisher's terms.
