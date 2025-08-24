# gpkg_fusion

`gpkg_fusion` es una herramienta en Python para fusionar múltiples archivos vectoriales (GeoPackage, Shapefile, GeoJSON) en un único GeoPackage. Soporta reproyección automática a un EPSG objetivo y evita conflictos de nombres de capas.

---

## Instalación

1. Clona o descarga el repositorio en tu máquina:  

```bash
git clone https://github.com/K3vin91/gpkg_fusion.git
cd gpkg_fusion
```

2. Instala las dependencias:  

```bash
py -m pip install geopandas fiona pyogrio
```

> No es necesario instalar el módulo en modo editable; simplemente ejecuta `gpkg_fusion.py`.

---

## Uso

Ejecuta el script desde la línea de comandos con `py -m gpkg_fusion`:

```bash
py -m gpkg_fusion --input_dir "RUTA_CARPETA_ENTRADA" --output_gpkg "RUTA_SALIDA.gpkg" --target_crs 32616
```

### Parámetros

- `--input_dir`: Carpeta que contiene los archivos vectoriales a fusionar.  
- `--output_gpkg`: Ruta del GeoPackage resultante.  
- `--target_crs`: (Opcional) EPSG para reproyección de todas las capas. Por ejemplo `32616`. Si se omite, las capas se conservan en su CRS original.  

---

## Características

- Fusiona múltiples archivos `.gpkg`, `.shp`, `.geojson` en un único GeoPackage.  
- Evita errores de duplicado creando nombres de capa únicos automáticamente.  
- Ignora archivos o capas vacías sin geometría.  
- Reproyecta capas al EPSG deseado si se indica.  
- Compatible con Python 3.10+ y librerías modernas de GeoDataFrame (`geopandas`, `fiona`, `pyogrio`).  

---

## Ejemplo

Supongamos que tienes una carpeta con varios GeoPackage y Shapefiles:

```
prueba_gpkg/
├─ AreaProtegidas.gpkg
├─ rios.shp
├─ zonas.geojson
```

Ejecuta:

```bash
py -m gpkg_fusion --input_dir "C:\Users\kevin\Documents\prueba_gpkg" --output_gpkg "C:\Users\kevin\Documents\fusionado.gpkg" --target_crs 32616
```

Se generará `fusionado.gpkg` con todas las capas, cada una con nombre único y reproyectada a EPSG:32616.

---

## Notas

- Si un GeoPackage de salida ya existe, se sobrescribe automáticamente.  
- Capas vacías o archivos sin geometría se ignoran y se reportan en consola.

