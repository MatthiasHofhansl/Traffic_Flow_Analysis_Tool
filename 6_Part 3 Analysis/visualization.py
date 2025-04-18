import pandas as pd
import matplotlib.pyplot as plt
import os

# === Pfade ===
CSV_PATH = os.path.join("3_Data for analysis", "wegetagebuch_karlsruhe_koordinaten.csv")
OUTPUT_PATH = os.path.join("7_Part 4 Graphics", "start_ziel_wege.jpg")

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

# === Plot vorbereiten
fig, ax = plt.subplots(figsize=(14, 10))
ax.axis('tight')
ax.axis('off')

# === Tabelle plotten
table = ax.table(
    cellText=weg_counts.values,
    colLabels=weg_counts.columns,
    cellLoc='center',
    loc='center'
)

table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.5)

# === Speichern
plt.savefig(OUTPUT_PATH, bbox_inches='tight')
plt.close()

print("✅ Tabelle erfolgreich erstellt und als JPG gespeichert.")