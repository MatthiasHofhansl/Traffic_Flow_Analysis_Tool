"""
- Öffnet die Datei wegetagebuch_karlsruhe_koordinaten.csv im Ordner 3_Data for analysis.
- Öffnet die Shapefile im Ordner 2_Shapefile folder (automatisch basierend auf der .shp-Datei).
- Wandelt Start- und Zielkoordinaten in GeoDataFrames um.
- Macht zwei räumliche Joins, um die Stadtteile zu bestimmen.
- Fügt die Stadtteilnamen in zwei neuen Spalten Stadtteil Start und Stadtteil Ziel ein.
- Überschreibt die ursprüngliche CSV-Datei.
"""
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os

# === Pfade ===
CSV_PATH = os.path.join("3_Data for analysis", "wegetagebuch_karlsruhe_koordinaten.csv")
SHAPEFILE_PATH = os.path.join("2_Shapefile folder", "Stadtteile_Karlsruhe.shp")

# === CSV laden ===
df = pd.read_csv(CSV_PATH)

# === Prüfen, ob Stadtteile schon existieren ===
stadtteile_existieren = "Stadtteil Start" in df.columns and "Stadtteil Ziel" in df.columns

# === Falls ja: nachfragen, ob neu berechnet werden soll ===
if stadtteile_existieren:
    user_input = input("Stadtteil-Spalten sind bereits vorhanden. Möchtest du sie neu berechnen und überschreiben? (j/n): ").strip().lower()
    if user_input != "j":
        print("Stadtteil-Zuordnung wird übersprungen.")
        df.to_csv(CSV_PATH, index=False)
        exit()
    else:
        print("Stadtteile werden neu berechnet und überschrieben.")

# === Shapefile laden ===
gdf_stadtteile = gpd.read_file(SHAPEFILE_PATH)
crs_stadtteile = gdf_stadtteile.crs

# === GeoDataFrame für Startorte ===
gdf_start = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df.start_lon, df.start_lat),
    crs="EPSG:4326"
).to_crs(crs_stadtteile)

# === GeoDataFrame für Zielorte ===
gdf_ziel = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df.ziel_lon, df.ziel_lat),
    crs="EPSG:4326"
).to_crs(crs_stadtteile)

# === Räumlicher Join Start ===
joined_start = gpd.sjoin(gdf_start, gdf_stadtteile, how="left", predicate="within")
neue_spalten_start = joined_start.columns.difference(df.columns).tolist()
stadtteil_start_col = neue_spalten_start[0] if neue_spalten_start else "Stadtteil Start"
df["Stadtteil Start"] = joined_start[stadtteil_start_col]

# === Räumlicher Join Ziel ===
joined_ziel = gpd.sjoin(gdf_ziel, gdf_stadtteile, how="left", predicate="within")
neue_spalten_ziel = joined_ziel.columns.difference(df.columns).tolist()
stadtteil_ziel_col = neue_spalten_ziel[0] if neue_spalten_ziel else "Stadtteil Ziel"
df["Stadtteil Ziel"] = joined_ziel[stadtteil_ziel_col]

# === Geometriespalte entfernen ===
df.drop(columns=["geometry"], inplace=True, errors="ignore")

# === CSV-Datei überschreiben ===
df.to_csv(CSV_PATH, index=False)
print("CSV-Datei mit Stadtteilen erfolgreich gespeichert.")