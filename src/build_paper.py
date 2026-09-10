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
    "FIG1": ("Figure 1.", "Composition against the aggregate, all 56 "
             "segmentation-by-year-pair tests. If a change in the mix of "
             "applicants accounted for the movement in the pooled approval "
             "rate, the points would lie on the dashed diagonal. They lie on "
             "the horizontal instead: 49 of 56 fall within ±0.5 pp of zero. "
             "Loan purpose is highlighted because it was the pre-registered "
             "axis."),
    "FIG2": ("Figure 2.", "The Breslow–Day p-value for the 2024–2025 tables, "
             "recounted at ten scales. Cell counts are divided by a constant "
             "and rounded, so the proportions are held and only the sample "
             "size falls. Loan purpose crosses conventional significance near "
             "10\u2075 applications and reaches p ≈ 10⁻³⁹⁹ at full scale; sex "
             "never crosses it. Below one hundredth of scale the per-cell "
             "rounding begins to distort the effect size, which is reported in "
             "Table 1."),
    "FIG3": ("Figure 3.", "Heterogeneity carried by each segmentation axis, "
             "as the ratio of the largest to the smallest stratum odds ratio. "
             "The hollow marker is the narrowest of the seven year-pairs and "
             "the filled marker the widest; 1× would mean every stratum moved "
             "alike. Sex and ethnicity are the only axes on which Breslow–Day "
             "ever fails to reject, and they are also the narrowest — an "
             "agreement between test and magnitude that does not hold for the "
             "other six."),
    "FIG4": ("Figure 4.", "Levels and movements are different questions. "
             "Left: approval rate by reported race in 2025, spanning 15.1 pp. "
             "Right: the change in that rate between 2024 and 2025, spanning "
             "2.6 pp. The homogeneity result of section 6 concerns the right "
             "panel only. Ethnicity behaves the same way, with a level spread "
             "of 9.2 pp and a movement spread of 0.5 pp."),
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
NARROW = {"FIG1"}

FIGFILES = {
    "FIGCOVER": "fig_cover",
    "FIG1": "fig1_composition", "FIG2": "fig2_scale",
    "FIG3": "fig3_axes",        "FIG4": "fig4_levels",
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
