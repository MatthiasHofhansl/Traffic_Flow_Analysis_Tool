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

# === Falls Spalten schon existieren → entfernen für saubere Neuberechnung
if "Stadtteil Start" in df.columns:
    df.drop(columns=["Stadtteil Start"], inplace=True)

if "Stadtteil Ziel" in df.columns:
    df.drop(columns=["Stadtteil Ziel"], inplace=True)

# === Shapefile einlesen
gdf_stadtteile = gpd.read_file(SHAPEFILE_PATH)
crs_stadtteile = gdf_stadtteile.crs  # z. B. EPSG:25832

# === GeoDataFrames für Start- und Zielorte erstellen
gdf_start = gpd.GeoDataFrame(
    df.copy(),
    geometry=gpd.points_from_xy(df.start_lon, df.start_lat),
    crs="EPSG:4326"
).to_crs(crs_stadtteile)

gdf_ziel = gpd.GeoDataFrame(
    df.copy(),
    geometry=gpd.points_from_xy(df.ziel_lon, df.ziel_lat),
    crs="EPSG:4326"
).to_crs(crs_stadtteile)

# === Räumlicher Join: Startorte
joined_start = gpd.sjoin(gdf_start, gdf_stadtteile, how="left", predicate="within")
df["Stadtteil Start"] = joined_start["NAME"]

# === Räumlicher Join: Zielorte
joined_ziel = gpd.sjoin(gdf_ziel, gdf_stadtteile, how="left", predicate="within")
df["Stadtteil Ziel"] = joined_ziel["NAME"]

# === Geometriespalte entfernen
df.drop(columns=["geometry"], inplace=True, errors="ignore")

# === Speichern
df.to_csv(CSV_PATH, index=False)
print("✔️ CSV-Datei erfolgreich mit Stadtteilen aktualisiert.")