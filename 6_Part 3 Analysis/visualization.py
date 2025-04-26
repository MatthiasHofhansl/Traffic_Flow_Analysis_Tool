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

# === XLSX-Formatierung (für Stadtteilbeziehungen)
wb = load_workbook(OUTPUT_XLSX_PATH)
ws = wb.active

# Kopfzeile fett und zentriert
for cell in ws[1]:
    cell.font = Font(bold=True)
    cell.alignment = Alignment(horizontal='center')

# Zellen zentrieren und Spaltenbreiten anpassen
for column_cells in ws.columns:
    max_length = 0
    column = column_cells[0].column_letter
    for cell in column_cells:
        if cell.value:
            max_length = max(max_length, len(str(cell.value)))
    ws.column_dimensions[column].width = max_length + 2
    for cell in column_cells:
        cell.alignment = Alignment(horizontal='center')

# Auto-Filter setzen
ws.auto_filter.ref = ws.dimensions

# Speichern der formatierten XLSX
wb.save(OUTPUT_XLSX_PATH)

# === NEU: Ranking der Stadtteile erstellen ===

# Start-Stadtteile zählen
start_ranking = df_valid["Stadtteil Start"].value_counts().reset_index()
start_ranking.columns = ["Stadtteil", "Anzahl Starts"]

# Ziel-Stadtteile zählen
ziel_ranking = df_valid["Stadtteil Ziel"].value_counts().reset_index()
ziel_ranking.columns = ["Stadtteil", "Anzahl Ziele"]

# Zusammenführen
ranking = pd.merge(start_ranking, ziel_ranking, on="Stadtteil", how="outer").fillna(0)
ranking["Anzahl Starts"] = ranking["Anzahl Starts"].astype(int)
ranking["Anzahl Ziele"] = ranking["Anzahl Ziele"].astype(int)

# Nach Starts oder Zielen sortieren (du kannst auch nach Summe sortieren, wenn du willst)
ranking = ranking.sort_values(by=["Anzahl Starts", "Anzahl Ziele"], ascending=False)

# === Ranking speichern
ranking.to_csv(RANKING_CSV_PATH, index=False, encoding='utf-8-sig')
ranking.to_excel(RANKING_XLSX_PATH, index=False)

# === XLSX-Formatierung (für Stadtteile-Ranking)
wb_rank = load_workbook(RANKING_XLSX_PATH)
ws_rank = wb_rank.active

# Kopfzeile fett und zentriert
for cell in ws_rank[1]:
    cell.font = Font(bold=True)
    cell.alignment = Alignment(horizontal='center')

# Zellen zentrieren und Spaltenbreiten anpassen
for column_cells in ws_rank.columns:
    max_length = 0
    column = column_cells[0].column_letter
    for cell in column_cells:
        if cell.value:
            max_length = max(max_length, len(str(cell.value)))
    ws_rank.column_dimensions[column].width = max_length + 2
    for cell in column_cells:
        cell.alignment = Alignment(horizontal='center')

# Auto-Filter setzen
ws_rank.auto_filter.ref = ws_rank.dimensions

# Speichern der formatierten Ranking-XLSX
wb_rank.save(RANKING_XLSX_PATH)

print("✅ Alle Dateien erfolgreich erstellt und gespeichert.")