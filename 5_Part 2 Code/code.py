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
SHAPEFILE_PATH = os.path.join("2_Shapefile folder", "stadtteile_ka.shp")

# === CSV laden ===
df = pd.read_csv(CSV_PATH)

# === Prüfen, ob Stadtteile schon existieren ===
stadtteile_existieren = "Stadtteil Start" in df.columns and "Stadtteil Ziel" in df.columns

# === Wenn vorhanden: Nutzer fragen, ob neu berechnet werden soll ===
if stadtteile_existieren:
    user_input = input("Stadtteil-Spalten sind bereits vorhanden. Möchtest du sie neu berechnen und überschreiben? (j/n): ").strip().lower()
    if user_input != "j":
        print("Stadtteil-Zuordnung wird übersprungen.")
        df.to_csv(CSV_PATH, index=False)
        exit()
    else:
        print("Stadtteile werden neu berechnet und überschrieben.")

# === Shapefile einlesen ===
gdf_stadtteile = gpd.read_file(SHAPEFILE_PATH)
crs_stadtteile = gdf_stadtteile.crs  # EPSG:25832

# === GeoDataFrames erstellen (Start und Ziel) ===
gdf_start = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df.start_lon, df.start_lat),
    crs="EPSG:4326"
).to_crs(crs_stadtteile)

gdf_ziel = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df.ziel_lon, df.ziel_lat),
    crs="EPSG:4326"
).to_crs(crs_stadtteile)

# === Räumlicher Join: Startorte
joined_start = gpd.sjoin(gdf_start, gdf_stadtteile, how="left", predicate="within")
df["Stadtteil Start"] = joined_start["st_name"]

# === Räumlicher Join: Zielorte
joined_ziel = gpd.sjoin(gdf_ziel, gdf_stadtteile, how="left", predicate="within")
df["Stadtteil Ziel"] = joined_ziel["st_name"]

# === Geometriespalte entfernen
df.drop(columns=["geometry"], inplace=True, errors="ignore")

# === Datei überschreiben
df.to_csv(CSV_PATH, index=False)
print("CSV-Datei erfolgreich mit Stadtteilen aktualisiert.")