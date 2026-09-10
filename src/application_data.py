"""
Datos de solicitudes hipotecarias de HMDA, vía el Data Browser del
FFIEC/CFPB. Público, sin clave y sin registro.

    https://ffiec.cfpb.gov/documentation/api/data-browser/

Se usa el endpoint `view/aggregations`, que devuelve la tabla cruzada ya
agregada en ~500 bytes. No hace falta bajar el fichero a nivel préstamo
(varios GB por año) porque el análisis solo necesita conteos por celda.
Dos advertencias de la API, ambas comprobadas:

  * exige filtro geográfico — no hay agregación nacional. Se pasan las 51
    jurisdicciones (50 estados + DC), y eso define la población del paper.
  * los filtros multivaluados hacen de eje de agrupación: pedir
    `loan_purposes=1,2,31,32,4,5` devuelve el cruce propósito x resultado.

Las respuestas quedan versionadas en data/hmda_aggregations/ para que el
análisis sea recomprobable sin volver a llamar a la API. Son conteos
públicos agregados, no microdatos.

Regla de la serie: NUNCA datos del empleador. Solo fuentes públicas.

LA TASA DE APROBACIÓN NO ES UN CAMPO. Es una definición sobre
`action_taken`, y la definición es parte del argumento del paper:

    numerador   = 1 (originado) + 2 (aprobado, no aceptado por el cliente)
    denominador = 1 + 2 + 3 (denegado)
    excluidos   = 4 (retirada), 5 (incompleta), 6 (comprada)

Se excluyen 4-6 porque la tasa debe medir decisiones del prestamista, y
una retirada no lo es. La alternativa (incluir retiradas) es común en la
práctica y cambia el nivel; va reportada en las limitaciones.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CACHE = DATA / "hmda_aggregations"

# 50 estados + DC. Territorios excluidos: la población del paper es esta.
STATES = ("AL,AK,AZ,AR,CA,CO,CT,DE,DC,FL,GA,HI,ID,IL,IN,IA,KS,KY,LA,ME,MD,"
          "MA,MI,MN,MS,MO,MT,NE,NV,NH,NJ,NM,NY,NC,ND,OH,OK,OR,PA,RI,SC,SD,"
          "TN,TX,UT,VT,VA,WA,WV,WI,WY")

PERIODS = list(range(2018, 2026))
PAIRS = list(zip(PERIODS, PERIODS[1:]))

# Ejes de segmentación, con los valores que se piden a la API. El orden es
# el del paper: primero lo que describe el préstamo, luego al solicitante.
SEGMENTATIONS = {
    "loan_purposes":        "1,2,31,32,4,5",
    "loan_types":           "1,2,3,4",
    "lien_statuses":        "1,2",
    "construction_methods": "1,2",
    "total_units":          "1,2,3,4",
    "races":                ("American Indian or Alaska Native,Asian,"
                             "Black or African American,"
                             "Native Hawaiian or Other Pacific Islander,White"),
    "sexes":                "Male,Female,Joint",
    "ethnicities":          "Hispanic or Latino,Not Hispanic or Latino,Joint",
}

# Etiquetas legibles. Los códigos numéricos son los del diccionario de
# campos de HMDA; los ejes demográficos ya vienen etiquetados por la API.
LABELS = {
    "loan_purposes": {"1": "Home purchase", "2": "Home improvement",
                      "31": "Refinancing", "32": "Cash-out refinancing",
                      "4": "Other purpose", "5": "Not applicable"},
    "loan_types": {"1": "Conventional", "2": "FHA", "3": "VA", "4": "RHS/FSA"},
    "lien_statuses": {"1": "First lien", "2": "Subordinate lien"},
    "construction_methods": {"1": "Site-built", "2": "Manufactured"},
    "total_units": {"1": "1 unit", "2": "2 units", "3": "3 units",
                    "4": "4 units"},
}

AXIS_LABELS = {
    "loan_purposes": "Loan purpose", "loan_types": "Loan type",
    "lien_statuses": "Lien status", "construction_methods": "Construction",
    "total_units": "Units", "races": "Race", "sexes": "Sex",
    "ethnicities": "Ethnicity",
}


def label(var, key):
    return LABELS.get(var, {}).get(key, key)


def table(var, year):
    """{segmento: (n, aprobadas)} para un eje y un año.

    n = a1 + a2 + a3 (decisiones);  aprobadas = a1 + a2.
    Lee de la caché versionada; fetch_sources.py la rellena.
    """
    path = CACHE / f"{var}_{year}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} no existe. Corre primero: python fetch_sources.py")
    cells = {}
    for a in json.loads(path.read_text(encoding="utf-8"))["aggregations"]:
        key = a.get(var)
        if key is None:                  # celda de total, sin desglose
            continue
        cells.setdefault(str(key), {})[a["actions_taken"]] = a["count"]
    out = {}
    for key, acts in cells.items():
        a1, a2, a3 = acts.get("1", 0), acts.get("2", 0), acts.get("3", 0)
        if a1 + a2 + a3 > 0:
            out[label(var, key)] = (a1 + a2 + a3, a1 + a2)
    return out


def pair(var, y0, y1):
    """Las dos tablas de un par de años, restringidas a estratos comunes."""
    t0, t1 = table(var, y0), table(var, y1)
    common = [s for s in t0 if s in t1]
    return ({s: t0[s] for s in common}, {s: t1[s] for s in common})


def rate(approved, n):
    """Tasa de aprobación. Devuelve None con denominador cero, para que un
    estrato vacío no se cuele como 0% en las agregaciones."""
    return approved / n if n else None
