import pandas as pd
import os
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter

# === Pfade ===
CSV_PATH = os.path.join("3_Data for analysis", "wegetagebuch_karlsruhe_koordinaten.csv")
OUTPUT_CSV_PATH = os.path.join("7_Part 4 Graphics", "Stadtteilbeziehungen_Wegeanzahl.csv")
OUTPUT_XLSX_PATH = os.path.join("7_Part 4 Graphics", "Stadtteilbeziehungen_Wegeanzahl.xlsx")
RANKING_CSV_PATH = os.path.join("7_Part 4 Graphics", "Stadtteile_Ranking.csv")
RANKING_XLSX_PATH = os.path.join("7_Part 4 Graphics", "Stadtteile_Ranking.xlsx")

# === Daten einlesen
df = pd.read_csv(CSV_PATH)

# === Nur gültige Kombinationen (keine NaNs)
df_valid = df.dropna(subset=["Stadtteil Start", "Stadtteil Ziel"])

# === Gruppieren und zählen (Start-Ziel-Beziehungen)
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

# === XLSX-Formatierung für Stadtteilbeziehungen
wb = load_workbook(OUTPUT_XLSX_PATH)
ws = wb.active

for cell in ws[1]:
    cell.font = Font(bold=True)
    cell.alignment = Alignment(horizontal='center')

for column_cells in ws.columns:
    max_length = 0
    column = column_cells[0].column_letter
    for cell in column_cells:
        if cell.value:
            max_length = max(max_length, len(str(cell.value)))
    ws.column_dimensions[column].width = max_length + 2
    for cell in column_cells:
        cell.alignment = Alignment(horizontal='center')

ws.auto_filter.ref = ws.dimensions
wb.save(OUTPUT_XLSX_PATH)

# === NEU: Separates Stadtteil-Ranking (Starts und Ziele getrennt)

# Start-Stadtteile zählen und sortieren
start_ranking = df_valid["Stadtteil Start"].value_counts().reset_index()
start_ranking.columns = ["Stadtteil", "Anzahl Starts"]

# Ziel-Stadtteile zählen und sortieren
ziel_ranking = df_valid["Stadtteil Ziel"].value_counts().reset_index()
ziel_ranking.columns = ["Stadtteil", "Anzahl Ziele"]

# Beide Rankings separat behandeln
# Zusammenfügen (linke Seite Start, rechte Seite Ziel)
ranking_df = pd.DataFrame()

max_len = max(len(start_ranking), len(ziel_ranking))

# Start-Ranking auffüllen
start_ranking = start_ranking.reindex(range(max_len))
# Ziel-Ranking auffüllen
ziel_ranking = ziel_ranking.reindex(range(max_len))

# Zusammenbauen
ranking_df["Start Stadtteil"] = start_ranking["Stadtteil"]
ranking_df["Anzahl Starts"] = start_ranking["Anzahl Starts"]
ranking_df["Ziel Stadtteil"] = ziel_ranking["Stadtteil"]
ranking_df["Anzahl Ziele"] = ziel_ranking["Anzahl Ziele"]

# === Ranking speichern
ranking_df.to_csv(RANKING_CSV_PATH, index=False, encoding='utf-8-sig')
ranking_df.to_excel(RANKING_XLSX_PATH, index=False)

# === XLSX-Formatierung für Ranking
wb_rank = load_workbook(RANKING_XLSX_PATH)
ws_rank = wb_rank.active

for cell in ws_rank[1]:
    cell.font = Font(bold=True)
    cell.alignment = Alignment(horizontal='center')

for column_cells in ws_rank.columns:
    max_length = 0
    column = column_cells[0].column_letter
    for cell in column_cells:
        if cell.value:
            max_length = max(max_length, len(str(cell.value)))
    ws_rank.column_dimensions[column].width = max_length + 2
    for cell in column_cells:
        cell.alignment = Alignment(horizontal='center')

ws_rank.auto_filter.ref = ws_rank.dimensions
wb_rank.save(RANKING_XLSX_PATH)

print("✅ Alle Dateien erfolgreich erstellt und gespeichert (mit getrennten Rankings für Starts und Ziele).")