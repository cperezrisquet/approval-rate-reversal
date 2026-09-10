# LinkedIn post

Publish `paper/Widening-by-Curvature.pdf` as a **native document** — never a
link, never a screenshot. Page one is the feed thumbnail.

**No Markdown** in the body: LinkedIn renders asterisks and underscores
literally. **No Unicode bold or superscripts** either — they break screen
readers.

**This entry needs more care than the others.** The subject touches fair
lending, and the two cautions in the body are not optional padding: both
inferences get drawn from these figures in practice and both are wrong. Do
not cut them to fit the character limit. Cut something else.

---

## Mechanics checklist

- [ ] PDF attached as a native document, not a link or an image
- [ ] First page of the PDF is the visual cover — it is the feed thumbnail
- [ ] Document title within **58 characters** (see below)
- [ ] Body has no Markdown and no Unicode bold characters
- [ ] **Both cautions present and adjacent** — neither one alone
- [ ] Links only in the **first comment**
- [ ] Second comment: summary in Spanish
- [ ] Posted Tuesday or Wednesday, 8–9 a.m. Dominican time
- [ ] Signed with the author's name; affiliation "Santo Domingo, Dominican
      Republic" — never the employer
- [ ] Spanish follow-up scheduled 4–5 days later
      (`linkedin-post-2-es.md`)

---

## Document title

Maximum **58 characters**. Shown in bold under the carousel.

    The gap widened 3.26 pp. The odds went the other way.   (53)

Alternatives within the limit:

    Same rule, different cost. Why a gap widens by itself.  (54)
    Widening by Curvature                                   (21)

---

## Post body — paste as is

Between 2021 and 2023 the mortgage approval gap between White and Black
applicants widened by 3.26 percentage points.

Measured in odds, Black applicants tightened 4 per cent less than White
applicants over the same period.

Both numbers are correct. They are different functions of the same change.

Lenders do not tighten by subtracting percentage points. They move a score
cutoff, a debt-to-income ceiling, a loan-to-value floor. That is a
multiplicative shift, and a multiplicative shift costs a different number of
percentage points depending on where each group started.

The arithmetic is easy to check. Halve the odds for a group sitting at 90 per
cent and it falls to 81.8, losing 8.2 points. Halve the odds for a group at 70
per cent and it falls to 53.8, losing 16.2. The distance between them goes
from 20 points to 28 with nobody treated differently. You cannot fall far when
you start near a ceiling.

So I built a counterfactual. Take one odds ratio, estimated across all strata
of an axis and never across the pair being examined so it cannot be tuned to
the answer, and apply it blindly to the 2021 starting points. Across four
pairs it reproduces between 46 and 128 per cent of each observed widening,
with absolute residuals between 0.09 and 0.90 points.

On White versus Black it over-predicts. A group-blind shift produces plus 4.15
points where plus 3.26 was observed.

Two things I want to say plainly, because both get inferred from figures like
these and both are wrong.

This does not show that differential treatment increased. Most of the widening
is reproduced by a shift that is blind to group by construction.

And it does not show that lending was equitable. The design has no
applicant-level controls for income, collateral or debt burden, so it cannot
compare like with like, and it says nothing about the level of any gap. Only
about how a gap moves when a system tightens. The 2021 gap itself, 12.33
points before any of this began, is not explained by curvature and is not
analysed in the paper.

What the paper argues is narrower. A percentage-point gap between groups is a
poor instrument for monitoring differential outcomes, because it responds to
where each group starts as well as to how each is treated. The same
institution will show a widening gap in a downturn and a narrowing one in a
recovery with its credit box untouched. An odds ratio with an interval does
not have that property, and it is what the underlying rule actually moves.

Paper, data and code in the first comment. Every API response behind every
figure is committed, so the numbers can be rechecked without calling
anything. Section 6.1 has a second result I had no room for here: the
standard test for this ranks applicant sex above race, and the magnitudes
rank it below.

---

## First comment — links

Paper (PDF, 9 pages), data and code:
github.com/cperezrisquet/approval-rate-reversal

Source: HMDA filings via the FFIEC Data Browser API, 50 states and DC.
Public, no key, no registration.
ffiec.cfpb.gov/data-browser/

The pre-registered hypothesis, and the record of it failing, are in
findings/ — committed before the results.

Entry one of this series, on active-user definitions that diverge in sign:
github.com/cperezrisquet/active-user-divergence

## Second comment — resumen en español

CIFRAS CORRECTAS, CONCLUSIONES FALSAS · 2

Entre 2021 y 2023 la brecha de aprobación hipotecaria entre solicitantes
blancos y negros se ensanchó 3,26 puntos. Medido en momios, los solicitantes
negros se endurecieron un 4 % menos. Las dos cifras son correctas.

Un endurecimiento idéntico cuesta más puntos porcentuales a quien parte más
lejos del 100 %, así que la brecha se ensancha sola. Eso NO demuestra que
hubiera más trato diferencial, y tampoco que el crédito fuera equitativo: el
diseño no tiene controles de solvencia. Lo que sí sostiene es que la brecha
en puntos porcentuales es el instrumento equivocado para vigilarla.
