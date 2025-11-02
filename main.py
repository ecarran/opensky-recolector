from fastapi import FastAPI
from fastapi.responses import FileResponse
from recolector import recolectar

app = FastAPI(title="API Recolector OpenSky LEMD")

@app.get("/")
def home():
    return {"mensaje": "API OpenSky-Barajas operativa. Usa /recolectar para ejecutar."}

@app.get("/recolectar")
def lanzar_recoleccion():
    """Ejecuta una recolección manual."""
    try:
        registros = recolectar()
        return {"status": "ok", "registros": registros}
    except Exception as e:
        return {"status": "error", "detalle": str(e)}

@app.get("/descargar")
def descargar_csv():
    """Descarga el CSV diario acumulado."""
    from pathlib import Path
    from datetime import datetime

    nombre = f"opensky_LEMD_{datetime.now().strftime('%Y%m%d')}.csv"
    path = Path("data/raw") / nombre
    if not path.exists():
        return {"error": "Aún no se ha generado el CSV de hoy."}
    return FileResponse(path, media_type='text/csv', filename=path.name)
