# LinkedIn post

Publish `paper/Significant-by-Volume.pdf` as a **native document** — never a
link, never a screenshot. LinkedIn renders it as a swipeable carousel and page
one is the feed thumbnail.

**No Markdown** in the body: LinkedIn renders asterisks and underscores
literally. **No Unicode bold or superscripts** either — they break screen
readers, which is why the body writes "10 to the minus 399" in words.

---

## Mechanics checklist

- [ ] PDF attached as a native document, not a link or an image
- [ ] First page of the PDF is the visual cover — it is the feed thumbnail
- [ ] Document title within **58 characters** (see below)
- [ ] Body has no Markdown and no Unicode bold characters
- [ ] Links only in the **first comment**
- [ ] Second comment: summary in Spanish
- [ ] Posted Tuesday or Wednesday, 8–9 a.m. Dominican time
- [ ] Signed with the author's name; affiliation "Santo Domingo, Dominican
      Republic" — never the employer
- [ ] Spanish follow-up scheduled 4–5 days later (`linkedin-post-2-es.md`)

---

## Document title

Shown in bold under the carousel; blank falls back to the filename. It is a
second hook, read by people who open the document before the text, so it has
to stand alone. Maximum **58 characters**.

    p = 1e-399 or p = 0.73. Same data, same segments.       (49)

Leading with the contradiction, because it is the whole paper in one line and
the two numbers are what nobody believes until they see the table.

Alternatives, all within the limit:

    Your test says the segments differ. That's your volume. (55)
    0 of 56 reversals. 53 of 56 significant. 1 finding.     (51)
    Significant by Volume                                   (21)

---

## Post body — paste as is

A statistical test on 17.9 million mortgage applications says the segments
differ, at p of about 10 to the minus 399.

The same data, counted at one thousandth of the scale, says p = 0.73. No
difference worth mentioning.

The segments did not change. Only how many rows I counted.

I went looking for Simpson's paradox in credit approval rates — the textbook
warning that an aggregate rate can fall while every segment inside it rises. I
wrote the hypothesis down before touching the data: a shift from home purchases
toward refinancing should drag the pooled rate down while each purpose improved
on its own.

It was false. Across 8 segmentation axes and 7 consecutive year-pairs of public
HMDA filings, 56 tests in all, the paradox never occurs. Not once. The
composition of demand moves the pooled approval rate by less than half a
percentage point in 49 of the 56 pairs.

What does occur is heterogeneity — the segments genuinely do not share a common
effect. The Breslow-Day test rejects a common odds ratio in 53 of 56 pairs, 47
of them below 10 to the minus 10. And that verdict is close to worthless,
because every pair carries between 13 and 37 million applications. At that
volume the test has power against differences far too small for anyone to act
on.

Run by a mid-sized lender on its own book, the same test reports homogeneity
for an axis a national aggregate screams about.

The fix is to stop reporting the test and report the magnitude, which does not
depend on volume: the ratio of the largest to the smallest segment odds ratio.
On these filings the eight axes span 1.00x to 2.19x, and the ranking is not the
one you would guess from a dashboard layout.

Three things I did not expect:

- Loan purpose carries the most heterogeneity at 2.19x, which is reasonable —
a cash-out refinancing and a home-improvement loan are different products.
- The spread between segments is larger than the pooled movement hiding it in
17 of 48 pairs. The aggregate routinely reports a number smaller than the
disagreement it conceals.
- Breaking the rate down by applicant sex adds essentially nothing to a pooled
movement. Breaking it down by loan purpose changes the story entirely.

One caveat I want stated plainly, because it is easy to misquote. All of this
is about year-over-year movements, not levels. Approval rate levels differ by
15.1 points across reported race in these filings. That gap is large, it is
extensively documented, and this paper says nothing about its causes. What is
nearly homogeneous is the change from one year to the next.

Paper, data and code in the first comment. The 64 API responses behind every
figure are committed with the repository, so anyone can recheck the numbers
without calling the API once.

---

## First comment — links

Paper (PDF, 9 pages), data and code:
github.com/cperezrisquet/approval-rate-reversal

Source: HMDA filings 2018-2025 via the FFIEC Data Browser API, 50 states and
DC. Public, no key, no registration.
ffiec.cfpb.gov/data-browser/

Entry one of this series, on active-user definitions that diverge in sign:
github.com/cperezrisquet/active-user-divergence

## Second comment — resumen en español

CIFRAS CORRECTAS, CONCLUSIONES FALSAS · 2

Busqué la paradoja de Simpson en tasas de aprobación de crédito. En 56 pruebas
sobre datos públicos no aparece ni una vez. Lo que sí aparece es que el test de
homogeneidad contesta sobre tu volumen de datos y no sobre tu negocio: los
mismos datos a 1/1000 de escala pasan de p = 1e-399 a p = 0.73.

La recomendación práctica: reportar la magnitud, no el p-valor.
