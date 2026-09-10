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
    "FIG1": ("Figure 1.", "TODO — the reversal: pooled approval rate against "
             "the same rate computed within each segment. Same applications, "
             "same outcome field, opposite direction."),
    "FIG2": ("Figure 2.", "TODO — decomposition of the change in the pooled "
             "rate into a within-segment component and a composition "
             "component."),
    "FIG3": ("Figure 3.", "TODO — how often the reversal occurs across "
             "segmentations and periods."),
    "FIG4": ("Figure 4.", "TODO — the standardised rate beside the two "
             "published readings."),
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

FIGFILES = {
    "FIGCOVER": "fig1_cover",
    "FIG1": "fig1_reversal",  "FIG2": "fig2_decomposition",
    "FIG3": "fig3_scan",      "FIG4": "fig4_standardized",
}

html = (ROOT / "paper" / "paper_template.html").read_text(encoding="utf-8")

for key, fname in FIGFILES.items():
    svg = load_svg(fname)
    # {{NAME_BARE}}: el SVG solo, sin figure ni caption (portada).
    html = html.replace("{{" + key + "_BARE}}", svg)
    label, text = CAPTIONS[key]
    block = (f'<figure>\n{svg}\n'
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
