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

# Dateien und Ordner
CSV_PATH = os.path.join("3_Data for analysis", "wegetagebuch_karlsruhe_koordinaten.csv")
SHAPEFILE_DIR = "2_Shapefile folder"

# Suche nach der .shp-Datei
shp_files = [f for f in os.listdir(SHAPEFILE_DIR) if f.endswith(".shp")]
if not shp_files:
    raise FileNotFoundError("Keine .shp-Datei im Shapefile-Ordner gefunden.")
shapefile_path = os.path.join(SHAPEFILE_DIR, shp_files[0])

# CSV einlesen
df = pd.read_csv(CSV_PATH)

# Shapefile einlesen
gdf_stadtteile = gpd.read_file(shapefile_path)

# Projektion der Shapefile merken
crs_stadtteile = gdf_stadtteile.crs

# Startkoordinaten als GeoDataFrame
gdf_start = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df.start_lon, df.start_lat),
    crs="EPSG:4326"  # WGS84
).to_crs(crs_stadtteile)

# Zielkoordinaten als GeoDataFrame
gdf_ziel = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df.ziel_lon, df.ziel_lat),
    crs="EPSG:4326"
).to_crs(crs_stadtteile)

# Raumlicher Join: Stadtteil Start
joined_start = gpd.sjoin(gdf_start, gdf_stadtteile, how="left", predicate="within")
stadtteil_start_col = joined_start.columns.difference(df.columns).tolist()[0]
df["Stadtteil Start"] = joined_start[stadtteil_start_col]

# Raumlicher Join: Stadtteil Ziel
joined_ziel = gpd.sjoin(gdf_ziel, gdf_stadtteile, how="left", predicate="within")
stadtteil_ziel_col = joined_ziel.columns.difference(df.columns).tolist()[0]
df["Stadtteil Ziel"] = joined_ziel[stadtteil_ziel_col]

# Geometrie-Spalte wieder entfernen
df.drop(columns=["geometry"], inplace=True, errors="ignore")

# CSV-Datei überschreiben
df.to_csv(CSV_PATH, index=False)
print("Datei erfolgreich mit Stadtteilen ergänzt.")