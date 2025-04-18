import geopandas as gpd

gdf = gpd.read_file("2_Shapefile folder/Stadtteile_Karlsruhe.shp")
print(gdf.columns)
print(gdf.head())