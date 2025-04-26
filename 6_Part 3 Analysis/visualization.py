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
MULTIMODAL_CSV_PATH = os.path.join("7_Part 4 Graphics and tables", "Multimodalität.csv")
MULTIMODAL_XLSX_PATH = os.path.join("7_Part 4 Graphics and tables", "Multimodalität.xlsx")

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

# === CSV und XLSX für Stadtteilbeziehungen
output_df.to_csv(OUTPUT_CSV_PATH, index=False, encoding='utf-8-sig')
output_df.to_excel(OUTPUT_XLSX_PATH, index=False)

# === Formatierung Excel (Stadtteilbeziehungen)
wb = load_workbook(OUTPUT_XLSX_PATH)
ws = wb.active
for cell in ws[1]:
    cell.font = Font(bold=True)
    cell.alignment = Alignment(horizontal='center')
for column_cells in ws.columns:
    max_length = max(len(str(cell.value)) for cell in column_cells if cell.value)
    ws.column_dimensions[column_cells[0].column_letter].width = max_length + 2
    for cell in column_cells:
        cell.alignment = Alignment(horizontal='center')
ws.auto_filter.ref = ws.dimensions
wb.save(OUTPUT_XLSX_PATH)

# === Stadtteil-Ranking erstellen
start_ranking = df_valid["Stadtteil Start"].value_counts().reset_index()
start_ranking.columns = ["Start Stadtteil", "Anzahl Starts"]

ziel_ranking = df_valid["Stadtteil Ziel"].value_counts().reset_index()
ziel_ranking.columns = ["Ziel Stadtteil", "Anzahl Ziele"]

max_len = max(len(start_ranking), len(ziel_ranking))
start_ranking = start_ranking.reindex(range(max_len))
ziel_ranking = ziel_ranking.reindex(range(max_len))

ranking_df = pd.DataFrame({
    "Start Stadtteil": start_ranking["Start Stadtteil"],
    "Anzahl Starts": start_ranking["Anzahl Starts"],
    "Ziel Stadtteil": ziel_ranking["Ziel Stadtteil"],
    "Anzahl Ziele": ziel_ranking["Anzahl Ziele"]
})

ranking_df.to_csv(RANKING_CSV_PATH, index=False, encoding='utf-8-sig')
ranking_df.to_excel(RANKING_XLSX_PATH, index=False)

wb_rank = load_workbook(RANKING_XLSX_PATH)
ws_rank = wb_rank.active
for cell in ws_rank[1]:
    cell.font = Font(bold=True)
    cell.alignment = Alignment(horizontal='center')
for column_cells in ws_rank.columns:
    max_length = max(len(str(cell.value)) for cell in column_cells if cell.value)
    ws_rank.column_dimensions[column_cells[0].column_letter].width = max_length + 2
    for cell in column_cells:
        cell.alignment = Alignment(horizontal='center')
ws_rank.auto_filter.ref = ws_rank.dimensions
wb_rank.save(RANKING_XLSX_PATH)

# === Analyse Zweck der Wege
zweck_valid = df.dropna(subset=["Zweck"])
zweck_counts = (
    zweck_valid["Zweck"].value_counts(normalize=True) * 100
).reset_index()
zweck_counts.columns = ["Zweck", "Prozentuale Verteilung"]
zweck_counts["Prozentuale Verteilung"] = zweck_counts["Prozentuale Verteilung"].round(2)

zweck_counts.to_csv(ZWECK_CSV_PATH, index=False, encoding='utf-8-sig')
zweck_counts.to_excel(ZWECK_XLSX_PATH, index=False)

wb_zweck = load_workbook(ZWECK_XLSX_PATH)
ws_zweck = wb_zweck.active
for cell in ws_zweck[1]:
    cell.font = Font(bold=True)
    cell.alignment = Alignment(horizontal='center')
for column_cells in ws_zweck.columns:
    max_length = max(len(str(cell.value)) for cell in column_cells if cell.value)
    ws_zweck.column_dimensions[column_cells[0].column_letter].width = max_length + 2
    for cell in column_cells:
        cell.alignment = Alignment(horizontal='center')
ws_zweck.auto_filter.ref = ws_zweck.dimensions
wb_zweck.save(ZWECK_XLSX_PATH)

# === Kreisdiagramm der Wegezwecke
farben_dict = {
    "Heimweg": "orchid",
    "Sport": "limegreen",
    "Schule/Uni": "navy",
    "Freizeit": "gold",
    "Arbeit": "deepskyblue",
    "Arztbesuch": "grey",
    "Begleitung": "lightgreen",
    "Erholung": "sandybrown",
    "Einkaufen": "darkred"
}
farben = [farben_dict.get(zweck, "lightgrey") for zweck in zweck_counts["Zweck"]]

fig, ax = plt.subplots(figsize=(10, 8))
ax.pie(
    zweck_counts["Prozentuale Verteilung"],
    labels=zweck_counts["Zweck"],
    autopct="%1.1f%%",
    startangle=140,
    colors=farben
)
ax.axis('equal')
plt.title("Prozentuale Verteilung der Wegezwecke")
plt.savefig(ZWECK_PIE_PATH, bbox_inches='tight')
plt.close()

# === Analyse Multimodalität (NEU, korrekt!)
multimodal_valid = df.dropna(subset=["Multimodal"])
# Vergleich in Kleinschreibung
multimodal_ja = (multimodal_valid["Multimodal"].str.lower() == "ja").sum()
gesamt = multimodal_valid.shape[0]
multimodal_prozent = round((multimodal_ja / gesamt) * 100, 2)
monomodal_prozent = round(100 - multimodal_prozent, 2)

# Tabelle erstellen
multimodal_df = pd.DataFrame({
    "Typ": ["Multimodal", "Monomodal"],
    "Prozentuale Verteilung": [multimodal_prozent, monomodal_prozent]
})

multimodal_df.to_csv(MULTIMODAL_CSV_PATH, index=False, encoding='utf-8-sig')
multimodal_df.to_excel(MULTIMODAL_XLSX_PATH, index=False)

wb_multi = load_workbook(MULTIMODAL_XLSX_PATH)
ws_multi = wb_multi.active
for cell in ws_multi[1]:
    cell.font = Font(bold=True)
    cell.alignment = Alignment(horizontal='center')
for column_cells in ws_multi.columns:
    max_length = max(len(str(cell.value)) for cell in column_cells if cell.value)
    ws_multi.column_dimensions[column_cells[0].column_letter].width = max_length + 2
    for cell in column_cells:
        cell.alignment = Alignment(horizontal='center')
ws_multi.auto_filter.ref = ws_multi.dimensions
wb_multi.save(MULTIMODAL_XLSX_PATH)

print("✅ Alle Dateien erfolgreich erstellt und gespeichert.")