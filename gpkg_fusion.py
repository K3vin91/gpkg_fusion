# gpkg_fusion.py
import os
import argparse
import geopandas as gpd
import fiona

def leer_capa(ruta, capa=None, epsg_destino=None):
    """Lee una capa de un archivo vectorial y reproyecta si es necesario."""
    gdf = gpd.read_file(ruta, layer=capa) if capa else gpd.read_file(ruta)
    if gdf.empty:
        return None
    if epsg_destino:
        gdf = gdf.to_crs(epsg=int(epsg_destino))
    return gdf

def obtener_nombre_unico(base, existentes):
    """Genera nombre único evitando duplicados en el GPKG de salida."""
    nombre = base
    i = 1
    while nombre in existentes:
        nombre = f"{base}_{i}"
        i += 1
    existentes.add(nombre)
    return nombre

def procesar_gpkg(ruta, salida, epsg_destino, capas_existentes):
    """Procesa todas las capas de un GPKG."""
    for capa in fiona.listlayers(ruta):
        gdf = leer_capa(ruta, capa, epsg_destino)
        if gdf is None:
            print(f"⚠️  Capa vacía ignorada: {ruta} -> {capa}")
            continue
        archivo_base = os.path.splitext(os.path.basename(ruta))[0]
        nombre_capa = obtener_nombre_unico(f"{archivo_base}_{capa}", capas_existentes)
        gdf.to_file(salida, layer=nombre_capa, driver="GPKG", mode="a")

def procesar_vector_simple(ruta, salida, epsg_destino, capas_existentes):
    """Procesa shapefile o geojson individual."""
    gdf = leer_capa(ruta, epsg_destino=epsg_destino)
    if gdf is None:
        print(f"⚠️  Archivo vacío ignorado: {ruta}")
        return
    archivo_base = os.path.splitext(os.path.basename(ruta))[0]
    nombre_capa = obtener_nombre_unico(archivo_base, capas_existentes)
    gdf.to_file(salida, layer=nombre_capa, driver="GPKG", mode="a")

def fusionar_vectores(carpeta, salida, epsg_destino=None):
    """Fusiona todos los vectores en un único GPKG."""
    if os.path.exists(salida):
        os.remove(salida)

    capas_existentes = set()

    for root, _, files in os.walk(carpeta):
        for file in files:
            ruta = os.path.join(root, file)
            ext = file.lower().split(".")[-1]

            if ext == "gpkg":
                procesar_gpkg(ruta, salida, epsg_destino, capas_existentes)
            elif ext in ["shp", "geojson", "json"]:
                procesar_vector_simple(ruta, salida, epsg_destino, capas_existentes)

    print(f"✅ Fusión completada en: {salida}")

def main():
    parser = argparse.ArgumentParser(description="Fusiona vectores en un GPKG único.")
    parser.add_argument("--input_dir", required=True, help="Carpeta con archivos vectoriales")
    parser.add_argument("--output_gpkg", required=True, help="Ruta del GeoPackage de salida")
    parser.add_argument("--target_crs", required=False, help="EPSG de reproyección, ej: 32616")
    args = parser.parse_args()

    fusionar_vectores(
        carpeta=args.input_dir,
        salida=args.output_gpkg,
        epsg_destino=args.target_crs
    )

if __name__ == "__main__":
    main()
