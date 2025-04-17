import pandas as pd
import requests
import time

# Mapbox API Key
MAPBOX_API_KEY = "pk.eyJ1IjoiemViYTEwMTEiLCJhIjoiY205bDZ5YWExMDJkZDJpczY4Zm0yNHBzZSJ9.Em0xTM5AR9yaJZeF-6yYHA"

# Eingabedatei (Wird erstmal überschritten)
CSV_FILE = "wegetagebuch_karlsruhe.csv"

def geocode_location(location, proximity="Karlsruhe, Germany"):
    """Geokodiert einen Ort über Mapbox, gibt (lat, lon) zurück oder (None, None) bei Fehler."""
    query = f"{location}, {proximity}"
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{query}.json"
    params = {
        "access_token": MAPBOX_API_KEY,
        "limit": 1,
        "language": "de"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data["features"]:
            coords = data["features"][0]["geometry"]["coordinates"]
            return coords[1], coords[0]  # (lat, lon)
    except Exception as e:
        print(f"Fehler beim Geokodieren von '{location}': {e}")

    return None, None

def main():
    # CSV einlesen
    df = pd.read_csv(CSV_FILE)

    # Neue Spalten vorbereiten
    start_lat, start_lon = [], []
    ziel_lat, ziel_lon = [], []

    for index, row in df.iterrows():
        start = row["Startort"]
        ziel = row["Zielort"]

        lat_s, lon_s = geocode_location(start)
        lat_z, lon_z = geocode_location(ziel)

        start_lat.append(lat_s)
        start_lon.append(lon_s)
        ziel_lat.append(lat_z)
        ziel_lon.append(lon_z)

        print(f"{index+1}/{len(df)}: {start} -> ({lat_s}, {lon_s}), {ziel} -> ({lat_z}, {lon_z})")
        time.sleep(0.2)  # um Rate-Limits zu vermeiden

    # Spalten anhängen
    df["start_lat"] = start_lat
    df["start_lon"] = start_lon
    df["ziel_lat"] = ziel_lat
    df["ziel_lon"] = ziel_lon

    # Datei überschreiben
    df.to_csv(CSV_FILE, index=False)
    print("CSV-Datei erfolgreich aktualisiert.")

if __name__ == "__main__":
    main()