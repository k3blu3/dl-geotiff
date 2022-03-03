"""
create_gif.py

A command line tool to create GIFs of stacks of time series
from the Descartes Labs platform.

Author: Krishna Karra, Chris Davis
"""

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from geotiff.utils.parse_inputs import (
    check_tif_file,
    check_geojson,
    check_resolution_resample,
    check_tilesize,
    check_products_bands,
    check_datetimes,
    check_nodata,
    check_num_workers,
    check_srs,
    check_gdal_mem,
    check_cutline,
    check_gs_bucket,
    check_remove_local,
    check_verbose,
)
from geotiff.utils.platform import (
    dump_scenes,
    dump_tiles,
    copy_to_gs
)
from geotiff.utils.gdal import (
    merge_tifs,
    build_mosaic,
    project_wgs,
    reproject_resample,
)

import sys
import os
import shutil
import datetime


def get_parsed_args():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "tif_file", type=str, help="Output GeoTIFF to create (.tif)"
    )
    parser.add_argument(
        "--product_id",
        type=str,
        help="Product ID on DL Platform",
        default="landsat:LC08:01:RT:TOAR",
    )
    parser.add_argument(
        "--bands", type=str, nargs="+", help="Bands", default=None
    )
    parser.add_argument(
        "--start_datetime", type=str, help="Start datetime", default=None
    )
    parser.add_argument(
        "--end_datetime", type=str, help="End datetime", default=None
    )
    parser.add_argument(
        "--geojson", help="Limit scenes to fall within this region", default=None
    )
    parser.add_argument(
        "--resolution", type=float, help="Specify a resolution (meters)", default=None
    )
    parser.add_argument(
        "--tilesize", type=int, help='Specify a tilesize (int)', default=None
    )
    parser.add_argument(
        "--resample", type=str, help="Specify a GDAL resampling algorithm", default=None
    )
    parser.add_argument(
        "--num_workers", type=int, help="Number of workers for Raster call", default=1
    )
    parser.add_argument(
        "--nodata", type=int, help="Nodata value to use in GeoTIFF", default=0
    )
    parser.add_argument(
        "--srs", type=str, help="Output spatial reference system", default=None
    )
    parser.add_argument(
        "--gdal_mem", type=int, help="Memory to use for gdalwarp in MB", default=None
    )
    parser.add_argument(
        "--cutline", type=str, help="Path to cutline to clip final TIF", default=None
    )
    parser.add_argument(
        "--gs_bucket", type=str, help="GCP Bucket to copy final TIF", default=None
    )
    parser.add_argument(
        "--remove_local", help="Remove TIF locally (only use if copying to bucket)", 
        action="store_true", default=False
    )
    parser.add_argument(
        "--verbose", help="Verbose output to terminal", action="store_true", default=False
    )

    return parser.parse_args()


def main():
    args = get_parsed_args()

    tif_file = check_tif_file(args.tif_file)
    geometry = check_geojson(args.geojson)
    product_id, bands = check_products_bands(args.product_id, args.bands)
    start_datetime, end_datetime = check_datetimes(args.start_datetime, args.end_datetime)
    resolution, resample = check_resolution_resample(args.resolution, args.resample)
    tilesize = check_tilesize(args.tilesize)
    num_workers = check_num_workers(args.num_workers)
    nodata = check_nodata(args.nodata)
    srs = check_srs(args.srs)
    gdal_mem = check_gdal_mem(args.gdal_mem)
    cutline = check_cutline(args.cutline)
    gs_bucket = check_gs_bucket(args.gs_bucket)
    remove_local = check_remove_local(args.remove_local)
    verbose = check_verbose(args.verbose)

    tmp_dir = os.path.join(os.path.expanduser('~'), 'tmp')
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
        if verbose:
            print('Created temporary directory {}'.format(tmp_dir))

    if tilesize is None:
        if verbose:
            print('Dumping scenes to temporary directory...')

        dump_scenes(product_id, 
                    bands, 
                    start_datetime, 
                    end_datetime, 
                    geometry,
                    tmp_dir, 
                    num_workers,
                    verbose)
    else:
        if verbose:
            print('Dumping tiles to temporary directory...')

        dump_tiles(product_id,
                   bands,
                   start_datetime,
                   end_datetime,
                   geometry,
                   resolution,
                   tilesize,
                   tmp_dir,
                   num_workers,
                   verbose)

    if verbose:
        print('Complete!\n')

    if verbose:
        print('Reprojecting GeoTIFFs to WGS84...')

    project_wgs(tmp_dir, verbose)

    if verbose:
        print('Complete!\n')

    if verbose:
        print('Building mosaic from GeoTIFFs with nodata of {}...'.format(nodata))

    build_mosaic(tmp_dir, nodata, verbose)

    if verbose:
        print('Complete!\n')

    if verbose:
        print('Merging all GeoTIFFs...')

    merge_tifs(tmp_dir, tif_file, verbose)

    shutil.rmtree(tmp_dir)
    if verbose:
        print('Removed directory {}'.format(tmp_dir))
    
    if resolution or srs:
        if verbose:
            print('Re-projecting and/or resampling...')

        reproject_resample(tif_file, 
                           nodata, 
                           cutline, 
                           resolution, 
                           resample, 
                           srs, 
                           num_workers, 
                           gdal_mem,
                           verbose)

        if verbose:
            print('Complete!\n')

    if gs_bucket:
        if verbose:
            print('Copying to gs bucket...')

        copy_to_gs(tif_file, gs_bucket, remove_local, verbose)

        if verbose:
            print('Complete!\n')

    print('*** Powered by the Descartes Labs platform with a healthy dose of GDAL ***')


if __name__ == "__main__":
    main()
