import pandas as pd
import os
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter

# === Pfade ===
CSV_PATH = os.path.join("3_Data for analysis", "wegetagebuch_karlsruhe_koordinaten.csv")
OUTPUT_CSV_PATH = os.path.join("7_Part 4 Graphics", "Stadtteilbeziehungen_Wegeanzahl.csv")
OUTPUT_XLSX_PATH = os.path.join("7_Part 4 Graphics", "Stadtteilbeziehungen_Wegeanzahl.xlsx")

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
output_df.to_csv(OUTPUT_CSV_PATH, index=False, encoding='utf-8-sig')

# === XLSX speichern
output_df.to_excel(OUTPUT_XLSX_PATH, index=False)

# === XLSX-Formatierung
wb = load_workbook(OUTPUT_XLSX_PATH)
ws = wb.active

# Kopfzeile fett formatieren
for cell in ws[1]:
    cell.font = Font(bold=True)
    cell.alignment = Alignment(horizontal='center')

# Alle Zellen zentriert und Spaltenbreiten anpassen
for column_cells in ws.columns:
    max_length = 0
    column = column_cells[0].column_letter  # A, B, C, ...
    for cell in column_cells:
        try:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))
        except:
            pass
    adjusted_width = max_length + 2
    ws.column_dimensions[column].width = adjusted_width
    for cell in column_cells:
        cell.alignment = Alignment(horizontal='center')

# Filter setzen
ws.auto_filter.ref = ws.dimensions

# Speichern der formatieren XLSX
wb.save(OUTPUT_XLSX_PATH)

print("✅ CSV- und formatierte XLSX-Datei erfolgreich erstellt und gespeichert.")