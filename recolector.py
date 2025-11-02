import requests
import csv
from datetime import datetime, timezone
from pathlib import Path

PARAMS = {
    "lamin": 40.2, "lomin": -3.8,
    "lamax": 40.6, "lomax": -3.3
}
URL_OPENSKY = "https://opensky-network.org/api/states/all"
DATA_DIR = Path("data/raw")
DATA_DIR.mkdir(parents=True, exist_ok=True)

def recolectar():
    """Consulta OpenSky y guarda datos en CSV diario."""
    r = requests.get(URL_OPENSKY, params=PARAMS, timeout=15)
    r.raise_for_status()
    data = r.json()
    states, t = data.get("states", []), data.get("time")
    hora_utc = datetime.fromtimestamp(t, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    filas = []
    for s in states or []:
        callsign = (s[1] or "").strip()
        country = s[2] or ""
        lon, lat, alt = s[5] or 0, s[6] or 0, s[7] or 0
        vel = (s[9] or 0) * 3.6
        vert = s[11]
        mov = (
            "Ascendiendo" if vert and vert > 1.5 else
            "Descendiendo" if vert and vert < -1.5 else
            "En tierra" if alt < 500 else "Nivelado"
        )
        filas.append({
            "timestamp_utc": hora_utc,
            "callsign": callsign,
            "country": country,
            "lat": round(lat, 4),
            "lon": round(lon, 4),
            "alt_m": int(alt),
            "vel_kmh": int(vel),
            "movimiento": mov
        })

    if filas:
        filename = f"opensky_LEMD_{datetime.now().strftime('%Y%m%d')}.csv"
        filepath = DATA_DIR / filename
        nuevo = not filepath.exists()
        with open(filepath, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=filas[0].keys())
            if nuevo:
                writer.writeheader()
            writer.writerows(filas)
        print(f"✅ {len(filas)} vuelos registrados ({hora_utc})")
    else:
        print("⚠️ No se detectaron vuelos en esta consulta.")
    return len(filas)

# Si se ejecuta directamente (modo cron)
if __name__ == "__main__":
    recolectar()









