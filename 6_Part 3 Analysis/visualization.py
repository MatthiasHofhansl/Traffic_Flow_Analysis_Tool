import pandas as pd
import os
import matplotlib.pyplot as plt
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter

# === Pfade ===
CSV_PATH = os.path.join("3_Data for analysis", "wegetagebuch_karlsruhe_koordinaten.csv")
OUTPUT_FOLDER = "7_Part 4 Graphics and tables"

# Hauptspeicherpfade
OUTPUT_CSV_PATH = os.path.join(OUTPUT_FOLDER, "Stadtteilbeziehungen_Wegeanzahl.csv")
OUTPUT_XLSX_PATH = os.path.join(OUTPUT_FOLDER, "Stadtteilbeziehungen_Wegeanzahl.xlsx")
RANKING_CSV_PATH = os.path.join(OUTPUT_FOLDER, "Stadtteile_Ranking.csv")
RANKING_XLSX_PATH = os.path.join(OUTPUT_FOLDER, "Stadtteile_Ranking.xlsx")
ZWECK_CSV_PATH = os.path.join(OUTPUT_FOLDER, "Verkehrsaufkommen (Wege)_Wegegründe.csv")
ZWECK_XLSX_PATH = os.path.join(OUTPUT_FOLDER, "Verkehrsaufkommen (Wege)_Wegegründe.xlsx")
ZWECK_PIE_PATH = os.path.join(OUTPUT_FOLDER, "Verkehrsaufkommen (Wege)_Wegegründe_PieChart.png")
MULTIMODAL_CSV_PATH = os.path.join(OUTPUT_FOLDER, "Multimodalität.csv")
MULTIMODAL_XLSX_PATH = os.path.join(OUTPUT_FOLDER, "Multimodalität.xlsx")
MODAL_SPLIT_CSV_PATH = os.path.join(OUTPUT_FOLDER, "Modal Split_Wege.csv")
MODAL_SPLIT_XLSX_PATH = os.path.join(OUTPUT_FOLDER, "Modal Split_Wege.xlsx")
MODAL_SPLIT_PIE_PATH = os.path.join(OUTPUT_FOLDER, "Modal Split_Wege.png")
MODAL_SPLIT_KM_CSV_PATH = os.path.join(OUTPUT_FOLDER, "Modal Split_Personenkilometer.csv")
MODAL_SPLIT_KM_XLSX_PATH = os.path.join(OUTPUT_FOLDER, "Modal Split_Personenkilometer.xlsx")
MODAL_SPLIT_KM_PIE_PATH = os.path.join(OUTPUT_FOLDER, "Modal Split_Personenkilometer.png")

# === Hilfsfunktion zur Excel-Formatierung
def format_excel(filepath):
    wb = load_workbook(filepath)
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
    wb.save(filepath)

# === Daten einlesen
df = pd.read_csv(CSV_PATH)

# === 1. Stadtteilbeziehungen
df_valid = df.dropna(subset=["Stadtteil Start", "Stadtteil Ziel"])
weg_counts = (
    df_valid.groupby(["Stadtteil Start", "Stadtteil Ziel"])
    .size()
    .reset_index(name="Anzahl Wege")
    .sort_values(by="Anzahl Wege", ascending=False)
)

mask_häufig = weg_counts["Anzahl Wege"] >= 20
weg_counts_häufig = weg_counts[mask_häufig]
weg_counts_selten = weg_counts[~mask_häufig]

restliche_wege_anzahl = weg_counts_selten["Anzahl Wege"].sum()

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

output_df.to_csv(OUTPUT_CSV_PATH, index=False, encoding='utf-8-sig')
output_df.to_excel(OUTPUT_XLSX_PATH, index=False)
format_excel(OUTPUT_XLSX_PATH)

# === 2. Stadtteile-Ranking
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
format_excel(RANKING_XLSX_PATH)

# === 3. Wegezwecke Analyse
zweck_valid = df.dropna(subset=["Zweck"])
zweck_counts = (
    zweck_valid["Zweck"].value_counts(normalize=True) * 100
).reset_index()
zweck_counts.columns = ["Zweck", "Prozentuale Verteilung"]
zweck_counts["Prozentuale Verteilung"] = zweck_counts["Prozentuale Verteilung"].round(2)

zweck_counts.to_csv(ZWECK_CSV_PATH, index=False, encoding='utf-8-sig')
zweck_counts.to_excel(ZWECK_XLSX_PATH, index=False)
format_excel(ZWECK_XLSX_PATH)

# === 4. Kreisdiagramm Wegezwecke
farben_dict_zwecke = {
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

farben = [farben_dict_zwecke.get(zweck, "lightgrey") for zweck in zweck_counts["Zweck"]]

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

# === 5. Multimodalität Analyse
multimodal_valid = df.dropna(subset=["Multimodal"])
multimodal_ja = (multimodal_valid["Multimodal"].str.lower() == "ja").sum()
gesamt = multimodal_valid.shape[0]
multimodal_prozent = round((multimodal_ja / gesamt) * 100, 2)
monomodal_prozent = round(100 - multimodal_prozent, 2)

multimodal_df = pd.DataFrame({
    "Typ": ["Multimodal", "Monomodal"],
    "Prozentuale Verteilung": [multimodal_prozent, monomodal_prozent]
})

multimodal_df.to_csv(MULTIMODAL_CSV_PATH, index=False, encoding='utf-8-sig')
multimodal_df.to_excel(MULTIMODAL_XLSX_PATH, index=False)
format_excel(MULTIMODAL_XLSX_PATH)

# === 6. Modal Split Wege (Anteile nach Wegen)
modal_split_valid = df.dropna(subset=["Verkehrsmittel"])
modal_split = (
    modal_split_valid["Verkehrsmittel"].value_counts(normalize=True) * 100
).reset_index()

modal_split.columns = ["Verkehrsmittel", "Prozentuale Verteilung"]
modal_split["Prozentuale Verteilung"] = modal_split["Prozentuale Verteilung"].round(2)

modal_split.to_csv(MODAL_SPLIT_CSV_PATH, index=False, encoding='utf-8-sig')
modal_split.to_excel(MODAL_SPLIT_XLSX_PATH, index=False)
format_excel(MODAL_SPLIT_XLSX_PATH)

# Farben Modal Split korrekt angepasst auf "zu Fuß"
farben_dict_modal_split = {
    "Auto": "red",
    "zu Fuß": "deepskyblue",
    "Fahrrad": "navy",
    "ÖPNV": "green",
    "Multimodal": "orange",
    "E-Scooter": "purple"
}

farben_modal = [farben_dict_modal_split.get(vm, "lightgrey") for vm in modal_split["Verkehrsmittel"]]

fig, ax = plt.subplots(figsize=(10, 8))
ax.pie(
    modal_split["Prozentuale Verteilung"],
    labels=modal_split["Verkehrsmittel"],
    autopct="%1.1f%%",
    startangle=140,
    colors=farben_modal
)
ax.axis('equal')
plt.title("Modal Split der Wege")
plt.savefig(MODAL_SPLIT_PIE_PATH, bbox_inches='tight')
plt.close()

# === 7. Modal Split Personenkilometer
modal_split_km = df.dropna(subset=["Verkehrsmittel", "Entfernung_km"])
modal_split_km_grouped = modal_split_km.groupby("Verkehrsmittel")["Entfernung_km"].sum()
modal_split_km_percent = (modal_split_km_grouped / modal_split_km_grouped.sum() * 100).reset_index()
modal_split_km_percent.columns = ["Verkehrsmittel", "Prozentuale Verteilung"]
modal_split_km_percent["Prozentuale Verteilung"] = modal_split_km_percent["Prozentuale Verteilung"].round(2)

modal_split_km_percent.to_csv(MODAL_SPLIT_KM_CSV_PATH, index=False, encoding='utf-8-sig')
modal_split_km_percent.to_excel(MODAL_SPLIT_KM_XLSX_PATH, index=False)
format_excel(MODAL_SPLIT_KM_XLSX_PATH)

farben_modal_km = [farben_dict_modal_split.get(vm, "lightgrey") for vm in modal_split_km_percent["Verkehrsmittel"]]

fig, ax = plt.subplots(figsize=(10, 8))
ax.pie(
    modal_split_km_percent["Prozentuale Verteilung"],
    labels=modal_split_km_percent["Verkehrsmittel"],
    autopct="%1.1f%%",
    startangle=140,
    colors=farben_modal_km
)
ax.axis('equal')
plt.title("Modal Split der Personenkilometer")
plt.savefig(MODAL_SPLIT_KM_PIE_PATH, bbox_inches='tight')
plt.close()

print("✅ Alle Dateien und Diagramme wurden erfolgreich erstellt und gespeichert.")