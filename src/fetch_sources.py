"""
Descarga los documentos fuente a data/. No se versionan en el repo:
pertenecen a sus editores y son de acceso libre.

    python fetch_sources.py

Fuente: HMDA vía el endpoint view/aggregations del Data Browser del
FFIEC/CFPB. Baja las 64 respuestas (8 ejes x 8 años) que alimentan el
análisis, unos 500 bytes cada una. Ya están versionadas en
data/hmda_aggregations/, así que esto solo hace falta para refrescarlas
o para comprobar que siguen dando lo mismo.
"""
import pathlib
import shutil
import time
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
# El endpoint exige filtro geográfico (no hay agregación nacional) y los
# filtros multivaluados hacen de eje de agrupación. Ver application_data.py.
AGG = "https://ffiec.cfpb.gov/v2/data-browser-api/view/aggregations"


def main():
    import urllib.parse
    from application_data import CACHE, PERIODS, SEGMENTATIONS, STATES

    CACHE.mkdir(parents=True, exist_ok=True)
    nuevos = fallos = 0
    for var, vals in SEGMENTATIONS.items():
        for year in PERIODS:
            dest = CACHE / f"{var}_{year}.json"
            if dest.exists():
                continue
            q = urllib.parse.urlencode({"years": year, "states": STATES,
                                        "actions_taken": "1,2,3", var: vals})
            # La API devuelve 503 de vez en cuando; reintento con espera.
            for intento in range(5):
                try:
                    dest.write_bytes(get(f"{AGG}?{q}", timeout=120))
                    print(f"  bajado     {dest.name}  "
                          f"({dest.stat().st_size:,} bytes)")
                    nuevos += 1
                    break
                except Exception as exc:               # noqa: BLE001
                    espera = 3 * 2 ** intento
                    print(f"  {dest.name}: {exc} — reintento en {espera}s")
                    time.sleep(espera)
            else:
                print(f"  FALLÓ      {dest.name}")
                fallos += 1

    total = len(SEGMENTATIONS) * len(PERIODS)
    print(f"\n  {nuevos} nuevos, {fallos} fallos, "
          f"{len(list(CACHE.glob('*.json')))}/{total} en caché")
    print(f"  Destino: {CACHE}")


if __name__ == "__main__":
    main()
