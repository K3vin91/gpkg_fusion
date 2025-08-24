import geopandas as gpd
import os
import fiona
import argparse

def leer_capa(ruta, capa=None, epsg_destino=None):
    gdf = gpd.read_file(ruta, layer=capa) if capa else gpd.read_file(ruta)
    if epsg_destino:
        # Acepta tanto "4326" como "EPSG:4326"
        if isinstance(epsg_destino, str) and epsg_destino.upper().startswith("EPSG:"):
            epsg_destino = int(epsg_destino.split(":")[1])
        gdf = gdf.to_crs(epsg=epsg_destino)
    return gdf

def obtener_nombre_unico(nombre_base, existentes):
    nombre = nombre_base
    i = 1
    while nombre in existentes:
        nombre = f"{nombre_base}_{i}"
        i += 1
    existentes.add(nombre)
    return nombre

def procesar_gpkg(ruta, salida, epsg_destino, capas_existentes):
    capas = fiona.listlayers(ruta)
    for capa in capas:
        gdf = leer_capa(ruta, capa, epsg_destino)
        nombre_capa = obtener_nombre_unico(capa, capas_existentes)
        gdf.to_file(salida, layer=nombre_capa, driver="GPKG")

def procesar_vector_simple(ruta, salida, epsg_destino, capas_existentes):
    capa_base = os.path.splitext(os.path.basename(ruta))[0]
    gdf = leer_capa(ruta, epsg_destino=epsg_destino)
    nombre_capa = obtener_nombre_unico(capa_base, capas_existentes)
    gdf.to_file(salida, layer=nombre_capa, driver="GPKG")

def fusionar_vectores(carpeta, salida, epsg_destino=None):
    if os.path.exists(salida):
        os.remove(salida)
    capas_existentes = set()
    for root, _, files in os.walk(carpeta):
        for file in files:
            ext = file.lower().split(".")[-1]
            ruta = os.path.join(root, file)
            if ext == "gpkg":
                procesar_gpkg(ruta, salida, epsg_destino, capas_existentes)
            elif ext in ["shp", "geojson", "json"]:
                procesar_vector_simple(ruta, salida, epsg_destino, capas_existentes)
    print(f"✅ Fusion completada en: {salida}")

def main():
    parser = argparse.ArgumentParser(description="Fusionar vectores en un solo GeoPackage")
    parser.add_argument("--input_dir", required=True, help="Carpeta con archivos vectoriales")
    parser.add_argument("--output_gpkg", required=True, help="Ruta del GeoPackage final")
    parser.add_argument("--target_crs", required=False, help="EPSG destino (ej. 4326)")
    args = parser.parse_args()

    fusionar_vectores(
        carpeta=args.input_dir,
        salida=args.output_gpkg,
        epsg_destino=args.target_crs
    )

if __name__ == "__main__":
    main()
