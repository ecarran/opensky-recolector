import requests
import csv
import time
from datetime import datetime, timezone
from pathlib import Path

# ==========================
# CONFIGURACIÓN
# ==========================

# Zona de interés: Madrid-Barajas (LEMD) y alrededores
PARAMS = {
    "lamin": 40.2,
    "lomin": -3.8,
    "lamax": 40.6,
    "lomax": -3.3
}

URL_OPENSKY = "https://opensky-network.org/api/states/all"
DATA_DIR = Path("data/raw")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ==========================
# FUNCIONES
# ==========================

def obtener_vuelos():
    """Descarga los vuelos activos sobre Barajas (con reintentos y timeout ampliado)."""
    for intento in range(3):
        try:
            r = requests.get(URL_OPENSKY, params=PARAMS, timeout=30)
            r.raise_for_status()
            data = r.json()
            return data.get("states", []), data.get("time")
        except Exception as e:
            print(f"⚠️ Intento {intento+1}/3 fallido: {e}")
            time.sleep(5)
    raise ConnectionError("No se pudo conectar con OpenSky tras 3 intentos.")

def clasificar_movimiento(vertical_rate, alt):
    """Clasifica el movimiento según velocidad vertical y altitud."""
    if vertical_rate is None:
        return "Desconocido"
    if vertical_rate > 1.5:
        return "Ascendiendo"
    elif vertical_rate < -1.5:
        return "Descendiendo"
    elif alt < 500:
        return "En tierra / estacionario"
    else:
        return "Nivelado"

def guardar_csv(filas):
    """Guarda los datos en un CSV diario acumulativo."""
    if not filas:
        print("⚠️ No se detectaron vuelos en esta consulta.")
        return 0

    filename = f"opensky_LEMD_{datetime.now().strftime('%Y%m%d')}.csv"
    filepath = DATA_DIR / filename
    nuevo = not filepath.exists()

    with open(filepath, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=filas[0].keys())
        if nuevo:
            writer.writeheader()
        writer.writerows(filas)

    print(f"✅ {len(filas)} vuelos registrados en {filepath.name}")
    return len(filas)

def recolectar():
    """Consulta OpenSky, guarda datos y devuelve nº de registros."""
    print("📡 Consultando OpenSky – área LEMD (sin autenticación, timeout 30s)...")
    try:
        states, t = obtener_vuelos()
        hora_utc = datetime.fromtimestamp(t, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        filas = []
        for s in states or []:
            callsign = (s[1] or "").strip()
            country = s[2] or ""
            lon = s[5] or 0
            lat = s[6] or 0
            alt = s[7] or 0
            vel = (s[9] or 0) * 3.6  # m/s → km/h
            vert = s[11]  # velocidad vertical (m/s)
            mov = clasificar_movimiento(vert, alt)

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

        return guardar_csv(filas)

    except Exception as e:
        print(f"❌ Error en la recolección: {e}")
        return 0


# ==========================
# EJECUCIÓN DIRECTA (modo cron o manual)
# ==========================

if __name__ == "__main__":
    recolectar()







