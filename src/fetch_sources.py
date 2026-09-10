"""
Descarga los documentos fuente a data/. No se versionan en el repo:
pertenecen a sus editores y son de acceso libre.

    python fetch_sources.py

La lista de fuentes está VACÍA a propósito: la fuente de la entrega #2
no está decidida. Ver data/README.md. La candidata (HMDA / FFIEC Data
Browser) queda abajo lista para descomentar.
"""
import pathlib
import shutil
import ssl
import subprocess
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)


def ssl_context():
    """Contexto TLS que funciona también en instalaciones de python.org
    sin el bundle de CA (macOS: /Applications/Python 3.x/Install
    Certificates.command)."""
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


CTX = ssl_context()


def get(url, timeout=120):
    """Descarga con urllib; si la verificación TLS falla, reintenta con curl,
    que usa el almacén de certificados del sistema."""
    try:
        with urllib.request.urlopen(url, timeout=timeout, context=CTX) as r:
            return r.read()
    except (ssl.SSLError, urllib.error.URLError) as exc:
        # urllib envuelve el SSLError dentro de un URLError, así que hay que
        # mirar la causa para no tragarse fallos de red genuinos.
        reason = getattr(exc, "reason", exc)
        if not isinstance(exc, ssl.SSLError) and not isinstance(reason, ssl.SSLError):
            raise
        if not shutil.which("curl"):
            raise
        out = subprocess.run(
            ["curl", "-sSL", "--fail", "--max-time", str(timeout), url],
            capture_output=True, check=True)
        return out.stdout
# ---------------------------------------------------------------- FUENTES
# TODO: fijar la fuente. Candidata — HMDA (Home Mortgage Disclosure Act),
# vía el Data Browser del FFIEC/CFPB: nivel solicitud, con resultado
# (action_taken) y variables de segmentación, sin clave y sin registro.
#
#   HMDA_URL = ("https://ffiec.cfpb.gov/v2/data-browser-api/view/csv"
#               "?years={year}&states=XX")
#
# Documentación del API y diccionario de campos:
#   https://ffiec.cfpb.gov/documentation/api/data-browser/
#   https://ffiec.cfpb.gov/documentation/publications/loan-level-datasets/
#
# Ojo con el tamaño: el CSV nacional de un año son varios GB. Filtrar por
# estado o condado en la propia consulta, no después.

CSVS = [
    # (url, nombre_local, etiqueta_para_el_log)
]

JSONS = [
    # (url, nombre_local, etiqueta_para_el_log)
]


def fetch(url, dest, label):
    if dest.exists():
        print(f"  ya existe  {dest.name}")
        return
    print(f"  bajando    {dest.name}  ({label})")
    dest.write_bytes(get(url))
    print(f"             {dest.stat().st_size:,} bytes")


def main():
    if not CSVS and not JSONS:
        print("No hay fuentes configuradas todavía.")
        print("Decide la fuente en data/README.md y rellena CSVS / JSONS.")
        return

    for group, items in (("Tablas", CSVS), ("Series", JSONS)):
        if not items:
            continue
        print(f"{group}:")
        for url, name, label in items:
            try:
                fetch(url, DATA / name, label)
            except Exception as exc:                   # noqa: BLE001
                print(f"  FALLÓ      {name}: {exc}")
                print(f"             {url}")

    print(f"\nDestino: {DATA}")
    print("El esquema que espera el análisis está documentado en "
          "src/application_data.py.")


if __name__ == "__main__":
    main()
