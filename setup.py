# setup.py
from setuptools import setup, find_packages

setup(
    name="gpkg_fusion",
    version="0.1.0",
    description="Herramienta simple para fusionar capas vectoriales (GPKG, SHP, GeoJSON) en un único GeoPackage",
    author="Kevin Irias",
    packages=find_packages(),
    install_requires=[
        "geopandas",
        "fiona",
        "shapely",
        "pyproj"
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "gpkg_fusion=gpkg_fusion:main",
        ],
    },
)
