# Source documents

The source documents are **not redistributed here**. They belong to their
publishers and are freely available at the links below. Run
[`src/fetch_sources.py`](../src/fetch_sources.py) to download them into this
directory, or fetch them by hand.

```bash
cd src && python fetch_sources.py
```

## Status: the source is not fixed yet

This entry needs application-level data with an approve/deny outcome and at
least two segmentation variables. What was checked:

| Source | Verdict |
|---|---|
| BCRD, *Boletín de Estadísticas Sistemas de Pago* | **No.** Publishes payments — stocks and flows of instruments. No applications, no approvals. It is the source of entry #1. |
| Superintendencia de Bancos, open data | **No.** ProUsuario complaints, inspections, sanctions, regulations. Nothing transactional and nothing about applications. |
| BCRD API (`apibcrd.bancentral.gov.do`) | **No.** Angular SPA, no obvious REST endpoints. |
| HMDA / FFIEC Data Browser | **Candidate.** See below. |

There is no public Dominican source for credit approval rates. Choosing HMDA
moves the series off Dominican data for one entry; that is a deliberate change
of register, not an oversight, and the paper should say so in section 2.

## Candidate — HMDA, via the FFIEC/CFPB Data Browser

Home Mortgage Disclosure Act filings. Application-level, annual, public, no key
and no registration. Every US mortgage application at a covered institution,
with its outcome and the applicant and loan attributes.

- Data Browser: <https://ffiec.cfpb.gov/data-browser/>
- API documentation: <https://ffiec.cfpb.gov/documentation/api/data-browser/>
- Loan-level dataset documentation and field dictionary:
  <https://ffiec.cfpb.gov/documentation/publications/loan-level-datasets/>

Query shape (filter in the query — the national CSV for a single year runs to
several GB):

```
https://ffiec.cfpb.gov/v2/data-browser-api/view/csv?years=2024&states=XX
```

### The outcome field

Approval rate is not a field; it is a definition built on `action_taken`, and
the definition is itself part of the paper's argument. Codes to verify against
the field dictionary for the filing year in use:

| Code | Meaning | In the rate? |
|---|---|---|
| 1 | Loan originated | numerator |
| 2 | Approved but not accepted by the applicant | numerator — the lender approved |
| 3 | Application denied | denominator only |
| 4 | Withdrawn by the applicant | **excluded** — no lender decision |
| 5 | File closed for incompleteness | **excluded** — no lender decision |
| 6 | Purchased loan | **excluded** — not an application |
| 7, 8 | Preapproval request denied / approved but not accepted | decide explicitly and state it |

Excluding codes 4–6 is the defensible reading: the rate should measure
decisions, and a withdrawal is not one. Report the alternative denominator in
the limitations section, since including withdrawals is common in practice and
changes the level.

### Segmentation variables

To be fixed in `SEGMENTATIONS` in
[`src/application_data.py`](../src/application_data.py). Candidates carried by
the loan-level file: `loan_purpose`, `loan_type`, `occupancy_type`,
`derived_dwelling_category`, `lei` (the filing institution), county, and the
binned income, loan-to-value and debt-to-income fields.

Pick the segmentation before looking at which one reverses. Searching every
combination for a reversal and reporting the one that appears is the mistake
the series argues against; the scan in section 5 reports the whole distribution
of results, not its maximum.

## Reproducibility note

Whatever source is chosen: record the vintage — the file, its publication date
and the filing year — here and in section 9. HMDA filings are revised, and a
paper that cannot name its vintage cannot be rechecked.
