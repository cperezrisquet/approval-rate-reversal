"""
Datos de solicitudes de crédito para el análisis de reversión de la tasa
de aprobación. Mismo criterio que la entrega #1: cada bloque cita su
fuente, tabla y página o campo; todo es público y reproducible sin
credenciales.

    FUENTE: pendiente de decidir. Ver data/README.md — la candidata es
    HMDA / FFIEC Data Browser (nivel solicitud, con resultado
    aprobado/denegado y variables de segmentación). No hay fuente pública
    dominicana con tasas de aprobación: el BCRD publica pagos, no
    solicitudes, y la Superintendencia de Bancos no publica nada
    transaccional.

Regla de la serie: NUNCA datos del empleador. Solo fuentes públicas.

Esquema esperado, una fila por celda (no por solicitud), que es la forma
en que las fuentes públicas agregan y la que basta para una reversión:

    period      str   etiqueta del período  ("2023", "2024Q1", ...)
    segment     str   estrato               (producto, canal, tramo, ...)
    n           int   solicitudes recibidas
    approved    int   solicitudes aprobadas   (approved <= n)

Cualquier variable adicional de segmentación entra como columna extra y
se declara en SEGMENTATIONS, para que el barrido de la sección 5 pueda
recorrerlas todas.
"""
import pathlib

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# Períodos comparados en el paper. TODO: fijar al vintage de la fuente.
PERIODS = []

# Segmentaciones sobre las que se busca la reversión. La primera es la del
# resultado 1; el resto alimentan el barrido del resultado 3.
SEGMENTATIONS = {
    # "product":  "TODO: descripción y campo de origen",
    # "channel":  "TODO",
    # "purpose":  "TODO",
}


def load_applications(filename=None):
    """Carga la tabla de solicitudes desde data/.

    Los documentos fuente no se versionan (ver data/README.md); hay que
    correr `python fetch_sources.py` antes de esto.
    """
    if filename is None:
        raise NotImplementedError(
            "TODO: fijar el archivo fuente en data/ y su parseo. "
            "Ver data/README.md.")
    path = DATA / filename
    if not path.exists():
        raise FileNotFoundError(
            f"{path} no existe. Corre primero: python fetch_sources.py")
    df = pd.read_csv(path)
    missing = {"period", "segment", "n", "approved"} - set(df.columns)
    if missing:
        raise ValueError(f"faltan columnas en {path.name}: {sorted(missing)}")
    return df


def rate(approved, n):
    """Tasa de aprobación. Devuelve None con denominador cero, para que un
    estrato vacío no se cuele como 0% en las agregaciones."""
    return approved / n if n else None
