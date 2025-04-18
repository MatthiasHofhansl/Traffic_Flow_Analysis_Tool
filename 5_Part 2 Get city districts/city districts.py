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

# === CSV laden
df = pd.read_csv(CSV_PATH)

# === Shapefile laden
gdf_stadtteile = gpd.read_file(SHAPEFILE_PATH)
crs_stadtteile = gdf_stadtteile.crs

# === Funktion für robusten Stadtteil-Join mit Fallbacks
def get_stadtteil_column(df_coords, lon_col, lat_col, crs_target, stadtteile_gdf, column_name):
    # Punkt-Geometrie erstellen
    gdf_points = gpd.GeoDataFrame(
        df_coords,
        geometry=gpd.points_from_xy(df_coords[lon_col], df_coords[lat_col]),
        crs="EPSG:4326"
    ).to_crs(crs_target)

    # 1. Versuch: within
    joined = gpd.sjoin(gdf_points, stadtteile_gdf, how="left", predicate="within")
    result = joined["NAME"]

    # 2. Versuch: intersects nur für fehlende
    missing = result[result.isna()].index
    if len(missing) > 0:
        joined_fallback = gpd.sjoin(gdf_points.loc[missing], stadtteile_gdf, how="left", predicate="intersects")
        result.update(joined_fallback["NAME"])

    # 3. Versuch: nearest für letzte ungelöste Fälle
    missing = result[result.isna()].index
    if len(missing) > 0:
        # Mittelpunkt aller Stadtteile
        stadtteile_centroids = stadtteile_gdf.copy()
        stadtteile_centroids["geometry"] = stadtteile_centroids.centroid

        nearest = gpd.sjoin_nearest(gdf_points.loc[missing], stadtteile_centroids, how="left", distance_col="dist")
        result.update(nearest["NAME"])

    return result

# === Stadtteile berechnen
df["Stadtteil Start"] = get_stadtteil_column(df, "start_lon", "start_lat", crs_stadtteile, gdf_stadtteile, "Stadtteil Start")
df["Stadtteil Ziel"] = get_stadtteil_column(df, "ziel_lon", "ziel_lat", crs_stadtteile, gdf_stadtteile, "Stadtteil Ziel")

# === Geometriespalte entfernen
df.drop(columns=["geometry"], inplace=True, errors="ignore")

# === Speichern
df.to_csv(CSV_PATH, index=False)
print("✅ Stadtteile mit Fallback-Strategie erfolgreich zugewiesen.")