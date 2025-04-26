import pandas as pd
import os

# === Pfade ===
CSV_PATH = os.path.join("3_Data for analysis", "wegetagebuch_karlsruhe_koordinaten.csv")
OUTPUT_PATH = os.path.join("7_Part 4 Graphics", "Stadtteilbeziehungen_Wegeanzahl.csv")

# === Daten einlesen
df = pd.read_csv(CSV_PATH)

# === Nur gültige Kombinationen (keine NaNs)
df_valid = df.dropna(subset=["Stadtteil Start", "Stadtteil Ziel"])

# === Gruppieren und zählen
weg_counts = (
    df_valid.groupby(["Stadtteil Start", "Stadtteil Ziel"])
    .size()
    .reset_index(name="Anzahl Wege")
    .sort_values(by="Anzahl Wege", ascending=False)
)

# === Trennung: häufige vs. seltene Verbindungen
mask_häufig = weg_counts["Anzahl Wege"] >= 20
weg_counts_häufig = weg_counts[mask_häufig]
weg_counts_selten = weg_counts[~mask_häufig]

# === Restliche Wege zusammenfassen
restliche_wege_anzahl = weg_counts_selten["Anzahl Wege"].sum()

# === DataFrame für Ausgabe vorbereiten
output_df = weg_counts_häufig.copy()

# Zeile für restliche Wege ergänzen, falls vorhanden
if restliche_wege_anzahl > 0:
    output_df = pd.concat([
        output_df,
        pd.DataFrame({
            "Stadtteil Start": ["Restliche Wege"],
            "Stadtteil Ziel": [""],
            "Anzahl Wege": [restliche_wege_anzahl]
        })
    ], ignore_index=True)

# === CSV speichern
output_df.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')

print("✅ Datei erfolgreich erstellt und als CSV gespeichert.")