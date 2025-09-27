# gpkg2fusion.py
import os
import argparse
import geopandas as gpd
import fiona
import sys
from pyproj import CRS

def leer_capa(ruta, capa=None, epsg_destino=None, capas_sin_crs=None):
    """Lee una capa de un archivo vectorial y reproyecta si es necesario."""
    gdf = gpd.read_file(ruta, layer=capa) if capa else gpd.read_file(ruta)
    if gdf.empty:
        return None
    if gdf.crs is None:
        if capas_sin_crs is not None:
            capas_sin_crs.append(capa or os.path.splitext(os.path.basename(ruta))[0])
    if epsg_destino:
        gdf = gdf.to_crs(epsg=epsg_destino)
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

def procesar_gpkg(ruta, salida, epsg_destino, capas_existentes, resumen, capas_sin_crs):
    """Procesa todas las capas de un GPKG."""
    for capa in fiona.listlayers(ruta):
        try:
            gdf = leer_capa(ruta, capa, epsg_destino, capas_sin_crs)
            if gdf is None:
                msg = f"⚠️ {ruta} -> {capa}: vacía, ignorada"
                resumen.append(msg)
                print(msg)
                continue
            archivo_base = os.path.splitext(os.path.basename(ruta))[0]
            nombre_capa = obtener_nombre_unico(f"{archivo_base}_{capa}", capas_existentes)
            gdf.to_file(salida, layer=nombre_capa, driver="GPKG", mode="a")
            msg = f"✅ {ruta} -> {capa}: exportada como {nombre_capa}"
            resumen.append(msg)
            print(msg)
        except Exception as e:
            msg = f"❌ {ruta} -> {capa}: falló → {e}"
            resumen.append(msg)
            print(msg)

def procesar_vector_simple(ruta, salida, epsg_destino, capas_existentes, resumen, capas_sin_crs):
    """Procesa shapefile o geojson individual."""
    try:
        gdf = leer_capa(ruta, epsg_destino=epsg_destino, capas_sin_crs=capas_sin_crs)
        if gdf is None:
            msg = f"⚠️ {ruta}: vacío, ignorado"
            resumen.append(msg)
            print(msg)
            return
        archivo_base = os.path.splitext(os.path.basename(ruta))[0]
        nombre_capa = obtener_nombre_unico(archivo_base, capas_existentes)
        gdf.to_file(salida, layer=nombre_capa, driver="GPKG", mode="a")
        msg = f"✅ {ruta}: exportado como {nombre_capa}"
        resumen.append(msg)
        print(msg)
    except Exception as e:
        msg = f"❌ {ruta}: falló → {e}"
        resumen.append(msg)
        print(msg)

def fusionar_vectores(carpeta, salida, epsg_destino=None):
    """Fusiona todos los vectores en un único GPKG y genera resumen TXT."""
    # Validación del CRS ingresado
    if epsg_destino:
        if not str(epsg_destino).isdigit():
            sys.exit(f"❌ ERROR: CRS ingresado inválido → {epsg_destino}")
        epsg_destino = int(epsg_destino)
        try:
            CRS.from_epsg(epsg_destino)  # valida que exista
        except Exception:
            sys.exit(f"❌ ERROR: CRS EPSG:{epsg_destino} no válido o inexistente")

    # Si el usuario dio solo una carpeta, crear archivo fusion.gpkg dentro
    if os.path.isdir(salida) or not salida.lower().endswith(".gpkg"):
        os.makedirs(salida, exist_ok=True)
        salida = os.path.join(salida, "fusion.gpkg")

    # Crear carpeta destino si no existe
    os.makedirs(os.path.dirname(salida), exist_ok=True)

    if os.path.exists(salida):
        os.remove(salida)

    capas_existentes = set()
    resumen = []
    capas_sin_crs = []
    total = 0
    exitosos = 0
    fallidos = 0

    for root, _, files in os.walk(carpeta):
        for file in files:
            ruta = os.path.join(root, file)
            ext = file.lower().split(".")[-1]
            total += 1
            if ext == "gpkg":
                procesar_gpkg(ruta, salida, epsg_destino, capas_existentes, resumen, capas_sin_crs)
                exitosos += 1
            elif ext in ["shp", "geojson"]:
                procesar_vector_simple(ruta, salida, epsg_destino, capas_existentes, resumen, capas_sin_crs)
                exitosos += 1
            else:
                msg = f"⚠️ {ruta}: formato no soportado, ignorado"
                resumen.append(msg)
                print(msg)
                fallidos += 1

    # Guardar resumen
    resumen_path = os.path.splitext(salida)[0] + "_resumen.txt"
    with open(resumen_path, "w", encoding="utf-8") as f:
        f.write("RESUMEN DE FUSIÓN DE VECTORES EN GPKG\n\n")
        f.write(f"Carpeta procesada: {carpeta}\n")
        f.write(f"Archivo de salida: {salida}\n\n")
        f.write(f"Total de capas procesadas: {total}\n")
        if capas_sin_crs:
            f.write(f"Capas sin CRS (requieren reproyección): {len(capas_sin_crs)}\n")
            f.write("\n".join(capas_sin_crs) + "\n")
        f.write(f"\nCapas exitosas: {exitosos}\n")
        f.write(f"Archivos ignorados/fallidos: {fallidos}\n")

    print(f"\n✅ Fusión completada en: {salida}")
    print(f"📝 Resumen guardado en: {resumen_path}")

def main():
    parser = argparse.ArgumentParser(description="Fusiona vectores en un GPKG único.")
    parser.add_argument("--input_dir", required=True, help="Carpeta con archivos vectoriales")
    parser.add_argument("--output_gpkg", required=True, help="Ruta del GeoPackage de salida o carpeta destino")
    parser.add_argument("--target_crs", required=False, help="EPSG de reproyección, ej: 32616")
    args = parser.parse_args()

    fusionar_vectores(
        carpeta=args.input_dir,
        salida=args.output_gpkg,
        epsg_destino=args.target_crs
    )

if __name__ == "__main__":
    main()
