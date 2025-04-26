import pandas as pd
import os
import matplotlib.pyplot as plt
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter

# === Pfade ===
CSV_PATH = os.path.join("3_Data for analysis", "wegetagebuch_karlsruhe_koordinaten.csv")
OUTPUT_CSV_PATH = os.path.join("7_Part 4 Graphics and tables", "Stadtteilbeziehungen_Wegeanzahl.csv")
OUTPUT_XLSX_PATH = os.path.join("7_Part 4 Graphics and tables", "Stadtteilbeziehungen_Wegeanzahl.xlsx")
RANKING_CSV_PATH = os.path.join("7_Part 4 Graphics and tables", "Stadtteile_Ranking.csv")
RANKING_XLSX_PATH = os.path.join("7_Part 4 Graphics and tables", "Stadtteile_Ranking.xlsx")
ZWECK_CSV_PATH = os.path.join("7_Part 4 Graphics and tables", "Verkehrsaufkommen (Wege)_Wegegründe.csv")
ZWECK_XLSX_PATH = os.path.join("7_Part 4 Graphics and tables", "Verkehrsaufkommen (Wege)_Wegegründe.xlsx")
ZWECK_PIE_PATH = os.path.join("7_Part 4 Graphics and tables", "Verkehrsaufkommen (Wege)_Wegegründe_PieChart.png")

# === Daten einlesen
df = pd.read_csv(CSV_PATH)

# === Nur gültige Kombinationen (keine NaNs bei Start und Ziel)
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

# === Separates Stadtteil-Ranking (Starts und Ziele getrennt)

# Start-Stadtteile zählen
start_ranking = df_valid["Stadtteil Start"].value_counts().reset_index()
start_ranking.columns = ["Start Stadtteil", "Anzahl Starts"]

# Ziel-Stadtteile zählen
ziel_ranking = df_valid["Stadtteil Ziel"].value_counts().reset_index()
ziel_ranking.columns = ["Ziel Stadtteil", "Anzahl Ziele"]

# Zusammenfügen (getrennte Spalten, gleiche Zeilenzahl)
max_len = max(len(start_ranking), len(ziel_ranking))
start_ranking = start_ranking.reindex(range(max_len))
ziel_ranking = ziel_ranking.reindex(range(max_len))

ranking_df = pd.DataFrame({
    "Start Stadtteil": start_ranking["Start Stadtteil"],
    "Anzahl Starts": start_ranking["Anzahl Starts"],
    "Ziel Stadtteil": ziel_ranking["Ziel Stadtteil"],
    "Anzahl Ziele": ziel_ranking["Anzahl Ziele"]
})

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

# === NEU: Analyse Zweck der Wege

# Nur gültige Zwecke verwenden
zweck_valid = df.dropna(subset=["Zweck"])

# Gruppieren und Prozent berechnen
zweck_counts = (
    zweck_valid["Zweck"].value_counts(normalize=True) * 100
).reset_index()

zweck_counts.columns = ["Zweck", "Prozentuale Verteilung"]

# Werte auf 2 Nachkommastellen runden
zweck_counts["Prozentuale Verteilung"] = zweck_counts["Prozentuale Verteilung"].round(2)

# === Zweck-Dateien speichern
zweck_counts.to_csv(ZWECK_CSV_PATH, index=False, encoding='utf-8-sig')
zweck_counts.to_excel(ZWECK_XLSX_PATH, index=False)

# === XLSX-Formatierung für Zweck
wb_zweck = load_workbook(ZWECK_XLSX_PATH)
ws_zweck = wb_zweck.active

for cell in ws_zweck[1]:
    cell.font = Font(bold=True)
    cell.alignment = Alignment(horizontal='center')

for column_cells in ws_zweck.columns:
    max_length = 0
    column = column_cells[0].column_letter
    for cell in column_cells:
        if cell.value:
            max_length = max(max_length, len(str(cell.value)))
    ws_zweck.column_dimensions[column].width = max_length + 2
    for cell in column_cells:
        cell.alignment = Alignment(horizontal='center')

ws_zweck.auto_filter.ref = ws_zweck.dimensions
wb_zweck.save(ZWECK_XLSX_PATH)

# === NEU: Kreisdiagramm der Wegezwecke

# Farben definieren
farben_dict = {
    "Heimweg": "orchid",         # ausgesucht: violett
    "Sport": "limegreen",        # ausgesucht: helles grün
    "Schule/Uni": "navy",        # Dunkelblau
    "Freizeit": "gold",          # Gelb
    "Arbeit": "deepskyblue",     # Hellblau
    "Arztbesuch": "grey",        # Grau
    "Begleitung": "lightgreen",  # Hellgrün
    "Erholung": "sandybrown",    # ausgesucht: sandfarben
    "Einkaufen": "darkred"       # Dunkelrot
}

# Farben für Plot aufbauen (nach Reihenfolge der Werte)
farben = [farben_dict.get(zweck, "lightgrey") for zweck in zweck_counts["Zweck"]]

# Plot erstellen
fig, ax = plt.subplots(figsize=(10, 8))
ax.pie(
    zweck_counts["Prozentuale Verteilung"],
    labels=zweck_counts["Zweck"],
    autopct="%1.1f%%",
    startangle=140,
    colors=farben
)
ax.axis('equal')  # Kreis soll rund sein
plt.title("Prozentuale Verteilung der Wegezwecke")

# Diagramm speichern
plt.savefig(ZWECK_PIE_PATH, bbox_inches='tight')
plt.close()

print("✅ Alle Dateien und Diagramme erfolgreich erstellt und gespeichert.")