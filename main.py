from fastapi import FastAPI
from fastapi.responses import JSONResponse
from recolector import recolectar

app = FastAPI(title="OpenSky-Barajas API")

@app.get("/")
def home():
    return {"mensaje": "API OpenSky-Barajas operativa. Usa /recolectar para ejecutar."}


@app.get("/recolectar")
def ejecutar_recolector():
    """
    Ejecuta el proceso de recolección de vuelos sobre el área LEMD
    y devuelve el número de registros guardados o el error detectado.
    """
    try:
        registros = recolectar()
        return JSONResponse({"status": "ok", "registros": registros})
    except Exception as e:
        return JSONResponse({"status": "error", "detalle": str(e)})



