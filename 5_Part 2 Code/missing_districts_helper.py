import pandas as pd
import os

# === Pfad zur Datei ===
CSV_PATH = os.path.join("3_Data for analysis", "wegetagebuch_karlsruhe_koordinaten.csv")

# === CSV laden ===
df = pd.read_csv(CSV_PATH)

# === Fälle ohne vollständige Zuordnung (NaN in Start oder Ziel)
fehlende_zuordnung = df[df["Stadtteil Start"].isna() | df["Stadtteil Ziel"].isna()]

# === Ergebnis anzeigen
anzahl = len(fehlende_zuordnung)
print(f"\n🚩 {anzahl} Einträge konnten nicht vollständig zugeordnet werden.\n")

# === Zeige relevante Infos
if anzahl > 0:
    print(fehlende_zuordnung[[
        "Startort", "Zielort", "start_lat", "start_lon", "ziel_lat", "ziel_lon",
        "Stadtteil Start", "Stadtteil Ziel"
    ]])
else:
    print("✅ Alle Einträge wurden erfolgreich Stadtteilen zugeordnet.")