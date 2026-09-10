# Sources

Everything here is public. No key, no registration, no proprietary or
institution-internal data at any stage.

## What is committed, and why

```
hmda_aggregations/                       64 API responses (8 axes × 8 years)
prousuario_reclamaciones_2020-2026.csv   the Dominican cross-check
```

Unusually for this series, the source data *is* versioned. The reason is that
it is small: the FFIEC aggregations endpoint returns a cross-tabulation of
counts in roughly 500 bytes, so the entire evidence base for a paper covering
8.6 to 9.3 million applications a year is about 32 KB of public aggregate
counts. Committing it means every number in the paper can be rechecked without
contacting the API, which is worth more than the convention of not
redistributing sources.

Refresh them with `python src/fetch_sources.py`, which skips what is already
present and retries the endpoint's intermittent 503s.

## 1. HMDA, via the FFIEC Data Browser

Filings under the Home Mortgage Disclosure Act. Application-level, annual,
public. Filing years **2018–2025**, retrieved **10 September 2026**.

- Data Browser: <https://ffiec.cfpb.gov/data-browser/>
- API documentation: <https://ffiec.cfpb.gov/documentation/api/data-browser/>
- Field dictionary: <https://ffiec.cfpb.gov/documentation/publications/loan-level-datasets/>

The endpoint used is `view/aggregations`, not the loan-level files. Two of its
behaviours shape the whole design, and both were established empirically:

1. **A geographic filter is mandatory.** There is no national aggregate; a
   request without `states`, `msamds`, `counties` or `leis` returns HTTP 400
   (`provide-only-msamds-or-states-or-counties-or-leis`). The 50 states and
   the District of Columbia are requested, and that set defines the paper's
   population. Territories are excluded.
2. **A multi-valued filter doubles as a grouping axis.** Requesting
   `loan_purposes=1,2,31,32,4,5` returns the purpose-by-outcome
   cross-tabulation rather than a filtered total. `years` does *not* behave
   this way — two years in one request collapse into one figure — so each year
   is a separate call.

Request shape:

```
https://ffiec.cfpb.gov/v2/data-browser-api/view/aggregations
  ?years=2025&states=AL,AK,...,WY&actions_taken=1,2,3&loan_purposes=1,2,31,32,4,5
```

### The approval rate is a definition, not a field

HMDA reports `action_taken`. The rate used throughout the paper is:

| Code | Meaning | In the rate? |
|---|---|---|
| 1 | Loan originated | numerator |
| 2 | Approved but not accepted by the applicant | numerator — the lender approved |
| 3 | Application denied | denominator only |
| 4 | Withdrawn by the applicant | **excluded** — no lender decision |
| 5 | File closed for incompleteness | **excluded** — no lender decision |
| 6 | Purchased loan | **excluded** — not an application |

Excluding 4 to 6 is the defensible reading: the rate should measure decisions,
and a withdrawal is not one. Including withdrawals is common in practice and
lowers the level materially; section 8 of the paper reports the consequence.
Codes 7 and 8 (preapproval requests) do not arise under the filters used.

### Segmentation axes

Eight, declared in `SEGMENTATIONS` in
[`src/application_data.py`](../src/application_data.py): `loan_purposes`,
`loan_types`, `lien_statuses`, `construction_methods`, `total_units`, `races`,
`sexes`, `ethnicities`.

**The credit-risk axes are not available through this endpoint.** Tested and
confirmed: `debt_to_income_ratios`, `loan_to_value_ratios`, `income_brackets`
and `applicant_ages` are all accepted with HTTP 200 and all **ignored** — the
response comes back split by `actions_taken` only, with no breakdown. Same for
`age_groups`. Those fields exist only in the loan-level files, several
gigabytes per filing year.

That is the binding limitation on everything in this repository: there are no
applicant-level controls for income, collateral or debt burden, and HMDA does
not publish credit scores at all. No causal reading of any result is
available.

The demographic fields are as reported by the filing institution, with
substantial non-response, and the strata are the API's own categories.

**On axis selection.** Every hypothesis in this repository was written down
before the data behind it were examined, and the two that failed are recorded
as such: [`../findings/01-hipotesis-preregistrada.md`](../findings/01-hipotesis-preregistrada.md)
(the composition mechanism) and
[`../findings/03-preregistro-endurecimiento.md`](../findings/03-preregistro-endurecimiento.md)
(the curvature mechanism, whose pooled prediction came out at r = −0.025).
Both were committed before the results they concern; the git history is the
evidence.
The remaining seven axes are reported as a complete distribution, never as
the maximum. Searching combinations for the one that behaves interestingly and
reporting that one is the anti-pattern this series argues against.

## 2. Superintendencia de Bancos de la República Dominicana — ProUsuario

Used only for the Dominican cross-check, not for any result in the paper.
Monthly counts of consumer complaints resolved in favour of or against the
user, from August 2020, segmented by sex.

<https://datos.gob.do/> → *Estadísticas de ProUsuario, 2020 - 2026*

This is the only public Dominican source with the shape the paper needs — a
decision rate with strata. It shows no reversal either (0 of 6 annual and 0 of
70 monthly pairs) and carries a single segmentation axis, so it cannot support
the sweep. See [`../findings/02-resultado-negativo.md`](../findings/02-resultado-negativo.md).

## What was ruled out

| Source | Verdict |
|---|---|
| BCRD, *Boletín de Estadísticas Sistemas de Pago* | Publishes payments — stocks and flows of instruments. No applications, no approvals. It is the source of entry #1 of this series. |
| Superintendencia de Bancos, other open data | Inspections, sanctions, regulations. Nothing about applications. |
| BCRD API (`apibcrd.bancentral.gov.do`) | Angular SPA, no usable REST endpoints. |

## Revisions

HMDA filings are revised. The vintage above is the one every figure in the
paper was computed from, and it is restated in section 9 of the paper.
