# Descartes Labs GeoTIFF Tool

A tool for creating GeoTIFFs from products on the Descartes Labs platform

## GDAL

You must have GDAL command line tools installed on your machine.

## Installation

1. Check this out
  * `git clone git@github.com:descarteslabs/geotiff; cd geotiff`
2. Create a virtualenv or conda environment, activate it (Python 3).
   You can alternatively install it to your base metal system Python.
  * `mkvirtualenv tiff; workon tiff`
  * `conda create -n tiff; conda activate tiff`
3. Install the package
  * `pip3 install .`

## Usage

You can run the tool with the `--help` flag to get a sense of the various options.

  * `dl-geotiff --help`

This will display the inputs required, and various options that can be set.

The tool works as follows:
1. All desired scenes from a product are dumped to a temporary directory (via DL)
2. The scenes are re-projected to WGS84 (via GDAL)
3. The scenes are merged to create a single GeoTIFF (via GDAL)
4. The temporary directory is removed
5. The scenes are warped and resampled to create the final GeoTIFF (via GDAL)

### Required Inputs

* `tif_file` : Name of output GeoTIFF to create (.tif)

### Settings

* `--product_id` : 	Product ID to pull from platform
			Default: `landsat:LC08:01:RT:TOAR`
* `--bands` :		Bands for product to pull
			If empty, all bands for product will be pulled
			Default: `None`
* `--start_datetime` : 	Start datetime to filter by
			Default: `None`
* `--end_datetime` : 	End datetime to filter by
			Note that if start/end are not provided, all dates for product will be pulled
			Default: `None`
* `--geojson` : 	GeoJSON file to filter scenes search by
			If not set, all scenes for product will be pulled
			Note that this is simply used as a coarse filter to limit the scenes search
			To actually clip your final GeoTIFF use --cutline
			Default: `None`
* `--resolution` : 	Output resolution for final GeoTIFF in meters
			Note that resampling is done using GDAL after merge of all scenes is complete
			If not set, the ouptut will be at the native resolution of the product
			Default: `None`
* `--resample` : 	Resampling algorithm to use understood by GDAL
			Default: `None`
* `--num_workers` : 	Number of concurrent workers to use during rasterization
			Default: `1`
* `--nodata` : 		Nodata value to use in GeoTIFF creation
			Default: `0`
* `--srs` :   		Spatial reference system (EPSG or proj4) for output GeoTIFF
			Note that if this isn't set, the output will be in WGS84 (EPSG:4326)
			Default: `None`
* `--gdal_mem` :  	Set the amount of memory to use for final gdalwarp operation in MB
			Default: `None`
* `--cutline` : 	Specify a cutline file understood by GDAL to clip final GeoTIFF
			Default: `None`
* `--gs_bucket` :	URL for google bucket to copy final GeoTIFF (gs://)
			Default: `None`
* `--remove_local` : 	Remove final GeoTIFF locally once it's been created
			Only use this if --gs_bucket is set
			Default: `None`
* `--verbose` :  	Enable verbose output
			Default: `None`
