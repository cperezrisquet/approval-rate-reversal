# Approved in Every Segment, Rejected Overall

Simpson reversals in credit approval rates. *[TODO: source and period.]*

Entry #2 in the series *Cifras correctas, conclusiones falsas* — analytical
anti-patterns in banking and fintech measurement, each entry self-contained.
Entry #1: [Same System, Opposite
Trends](https://github.com/cperezrisquet/active-user-divergence).

**Status: scaffold.** The estimators are written and tested; the data source is
not fixed yet. See [Open decisions](#open-decisions).

**Paper:** `paper/Approved-in-Every-Segment.pdf` *(not built yet)*

## The claim

An approval rate computed over a pooled population can fall while the approval
rate of every segment inside it rises. Both numbers are correct: the pooled
rate is partly a statement about who applied, not about how applications were
decided. This entry measures how large that effect is in a real application
file, how often it flips the sign, and what a dashboard should publish instead.

## Headline findings

*Nothing here until the analysis runs. Each row must be reproducible from this
repository.*

| Finding | Result |
|---|---|
| Pooled approval rate, [period] | **[TODO]** |
| Same rate, within every segment | **[TODO]** |
| Share of the pooled change attributable to application mix | **[TODO]** |
| Period–segmentation pairs where the sign reverses | **[TODO]** |
| Directly standardised rate vs. published rate | **[TODO]** |

## Open decisions

1. **The data source.** There is no public Dominican source for approval
   rates: the BCRD publishes payments, not applications, and the
   Superintendencia de Bancos publishes complaints and sanctions, nothing
   transactional. The leading candidate is **HMDA** (Home Mortgage Disclosure
   Act) through the FFIEC/CFPB Data Browser — application-level, with an
   outcome field and several segmentation variables, no key and no
   registration. It moves the series off Dominican data, which is a change of
   register worth making deliberately.
2. **The novelty.** Simpson's paradox in lending data is not itself new. The
   contribution has to be the measurement — how much of a reported approval-rate
   movement is mix, how often the sign flips in practice, and which corrected
   indicator survives a change of weighting scheme.
3. **The title** follows the finding, not the other way round. The working
   title fits LinkedIn's 58-character document-title limit (43), so it can
   stand if the finding holds.

## Data sources

All public. No proprietary or institution-internal data is used at any stage,
and none is required to reproduce any figure. Links, tables and the field each
series comes from go in [`data/README.md`](data/README.md); the source
documents are **not redistributed in this repository**.

## Reproducing

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cd src
python analysis.py --selftest   # verifies the estimators on a synthetic case
python fetch_sources.py         # downloads the source documents into data/
python analysis.py              # results 1-4, printed to stdout
python figures.py               # regenerates figures/ as SVG + PNG
python build_paper.py           # assembles paper/paper.html
```

To rebuild the PDF from the assembled HTML:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf=paper/Approved-in-Every-Segment.pdf \
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
| `homogeneity` | Breslow–Day test — whether the strata share a common odds ratio at all. This is the test that decides whether pooling is legitimate, and it is what keeps the paper from resting on one anecdotal pair of periods. |

`python analysis.py --selftest` runs them against a synthetic two-stratum case
with a known reversal, asserts that the decomposition identity closes, and
checks the hand-written Mantel–Haenszel estimator against
`statsmodels.stats.contingency_tables.StratifiedTable` to 1e-12. The
hand-written version stays: in a paper about how definitions produce figures,
the arithmetic has to be on the page, and statsmodels is the check on it.

## Layout

```
src/     application_data.py  source series + expected schema
         analysis.py          estimators + results 1-4
         figures.py           figure generation
         build_paper.py       assembles HTML from template + SVGs
         fetch_sources.py     downloads the source documents
paper/   template, assembled HTML, PDF
figures/ SVG (vector, used in the paper) and PNG
data/    links to the sources (the documents themselves are not versioned)
```

## License

Code under MIT. The paper text is the author's. Source data remains subject to
its publisher's terms.
