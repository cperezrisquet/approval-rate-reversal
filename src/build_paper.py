"""Ensambla el paper: inserta los SVG y los metadatos en la plantilla."""
import re, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

AUTHOR = "Dr. Sc. Carlos Pérez Risquet"
AFFIL  = "Santo Domingo, Dominican Republic"
EMAIL  = "cperezrisquet@gmail.com"
DATE   = "September 2026"
REPO   = "github.com/cperezrisquet/approval-rate-reversal"

CAPTIONS = {
    "FIGCOVER": ("", ""),
    "FIG1": ("Figure 1.", "Change in the percentage-point approval gap, "
             "2021–2023, for the four large-stratum pairs. The hollow marker "
             "is what a single group-blind odds shift applied to the 2021 "
             "baselines produces; ψ is estimated by Mantel–Haenszel across all "
             "strata of the axis, never across the pair, so the counterfactual "
             "cannot be fitted to the gap it explains. It over-predicts on "
             "White versus Black and under-predicts on the other three."),
    "FIG2": ("Figure 2.", "The same tightening on the multiplicative scale: "
             "odds ratio 2021→2023 by reported race, with 95 % Woolf "
             "intervals, ordered by the estimate. Lower means tightened more. "
             "The dashed line is the common shift of 0.5557 that Figure 1 "
             "uses. No monotone description of these five estimates survives, "
             "which is why the paper reports all of them rather than a "
             "comparison."),
    "FIG3": ("Figure 3.", "The mechanism. Percentage points lost to a single "
             "odds shift of ψ = 0.5557, as a function of the rate a group "
             "starts from — the function r(1−r)(1−ψ)/(1−r+ψr), zero at both "
             "ends and maximal at 57.2 %. Markers are the five race strata at "
             "their 2021 baselines. White starts at 86.0 % and loses 8.66 pp; "
             "Black or African American starts at 73.7 % and loses 12.82 pp. "
             "The 4.15 pp between them requires no group to be treated "
             "differently."),
    "FIG4": ("Figure 4.", "The same three demographic axes ranked two ways. "
             "On the left, by the Breslow–Day test of whether their strata "
             "share a common shift; on the right, by the magnitude of the "
             "departure from one. Sex leads the test by 321 orders of "
             "magnitude and trails the magnitude. The ranking the test "
             "produces is driven by sample size and degrees of freedom, not by "
             "how unequally the tightening landed."),
}

def load_svg(name):
    """Lee el SVG y limpia el preámbulo XML para inline en HTML."""
    path = ROOT / "figures" / f"{name}.svg"
    svg = path.read_text(encoding="utf-8")
    svg = re.sub(r"<\?xml[^>]*\?>", "", svg)
    svg = re.sub(r"<!DOCTYPE[^>]*>", "", svg)
    svg = re.sub(r'(<svg[^>]*?)\swidth="[\d.]+pt"', r"\1", svg)
    svg = re.sub(r'(<svg[^>]*?)\sheight="[\d.]+pt"', r"\1", svg)
    return svg.strip()

# Figuras de aspecto cuadrado: llevan tope de ancho en la plantilla.
# Ninguna de esta entrega lo es.
NARROW = set()

FIGFILES = {
    "FIGCOVER": "fig_cover",
    "FIG1": "fig1_gaps",       "FIG2": "fig2_forest",
    "FIG3": "fig3_curvature",  "FIG4": "fig4_inversion",
}

html = (ROOT / "paper" / "paper_template.html").read_text(encoding="utf-8")

for key, fname in FIGFILES.items():
    svg = load_svg(fname)
    # {{NAME_BARE}}: el SVG solo, sin figure ni caption (portada).
    html = html.replace("{{" + key + "_BARE}}", svg)
    label, text = CAPTIONS[key]
    cls = ' class="narrow"' if key in NARROW else ''
    block = (f'<figure{cls}>\n{svg}\n'
             f'<figcaption><strong>{label}</strong> {text}</figcaption>\n</figure>')
    html = html.replace("{{" + key + "}}", block)

for key, val in [("AUTHOR", AUTHOR), ("AFFIL", AFFIL), ("EMAIL", EMAIL),
                 ("DATE", DATE), ("REPO", REPO)]:
    html = html.replace("{{" + key + "}}", val)

leftover = re.findall(r"\{\{(\w+)\}\}", html)
if leftover:
    sys.exit(f"ERROR: placeholders sin sustituir: {set(leftover)}")

out = ROOT / "paper" / "paper.html"
out.write_text(html, encoding="utf-8")
print(f"OK -> {out}  ({len(html):,} bytes)")

# El esqueleto arranca lleno de [TODO: ...]; avisar mientras queden, para no
# imprimir un PDF con marcadores dentro.
todos = re.findall(r"\[TODO[^\]]*\]", html)
if todos:
    print(f"AVISO: {len(todos)} marcadores [TODO] siguen en el documento. "
          f"No imprimir el PDF todavía.")
