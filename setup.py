from setuptools import setup, find_packages

setup(
    name="geotiff",
    description="Create GeoTIFF from DL Platform",
    version="0.0.6",
    packages=find_packages(),
    entry_points={"console_scripts": ["dl-geotiff=geotiff:main"]},
    setup_requires=["setuptools>40"],
    install_requires=[
        "descarteslabs[complete]>=0.25.0",
    ],
)
