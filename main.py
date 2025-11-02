from fastapi import FastAPI, Request
import requests
from fastapi.responses import JSONResponse

app = FastAPI(title="OpenSky Relay (Render)")

OPENSKY_URL = "https://opensky-network.org/api/states/all"

@app.get("/")
def home():
    return {"status": "ok", "message": "Relay operativo en Render (FastAPI)"}

@app.get("/opensky")
def relay(request: Request):
    params = dict(request.query_params)
    try:
        r = requests.get(OPENSKY_URL, params=params, timeout=15)
        r.raise_for_status()
        return JSONResponse(r.json())
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


