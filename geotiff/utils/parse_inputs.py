"""
parse_inputs.py

Parse command line inputs, and return useful parameters.
"""

# define imports
from datetime import datetime
import os
import json

import descarteslabs as dl


def check_tif_file(tif_file):
    try:
        assert tif_file.endswith(".tif")
    except:
        raise ValueError("Output file must end in .tif")

    tif_file = os.path.join(os.path.expanduser('~'), tif_file)

    return tif_file


def check_geojson(geojson):
    if geojson:
        try:
            with open(geojson, "r") as f:
                geojson_dict = json.load(f)
        except:
            geojson_dict = dl.places.shape(geojson)

        if "features" in geojson_dict:
            if len(geojson_dict["features"]) > 1:
                print(
                    "Warning! Found {0} features, but only taking first!".format(
                        len(geojson_dict["features"])
                    )
                )
            geojson = geojson_dict["features"][0]["geometry"]
        elif "geometry" in geojson_dict:
            geojson = geojson_dict["geometry"]
        else:
            geojson = geojson_dict
    
    return geojson


def check_resolution_resample(resolution, resample):
    try:
        if resolution:
            options = ['near',
                       'bilinear',
                       'cubic',
                       'cubicspline',
                       'lanczos',
                       'average',
                       'mode',
                       'max',
                       'min',
                       'med',
                       'q1',
                       'q3']
            assert(resample in options)
    except:
        raise ValueError('Resolution {} and/opr resample {} are invalid!'.format(resolution,
                                                                                 resample))

    return resolution, resample


def check_tilesize(tilesize):
    return tilesize
            

def check_products_bands(product_id, bands):
    try:
        _ = dl.metadata.get_product(product_id)
    except:
        raise ValueError("Product {} not found!".format(product_id))

    if bands:
        try:
            product_bands_list = dl.metadata.bands(product_id)
            drv_bands_list = dl.metadata.derived_bands()

            product_bands = [b["name"] for b in product_bands_list]
            drv_bands = [b["name"] for b in drv_bands_list]

            avail_bands = product_bands + drv_bands

            assert set(bands).issubset(set(avail_bands))

        except:
            raise ValueError("Bands {} are not valid!".format(bands))

    return product_id, bands


def check_datetimes(start_datetime, end_datetime):
    try:
        if start_datetime:
            if "T" in start_datetime:
                start = datetime.strptime(start_datetime, "%Y-%m-%dT%H:%M:%S")
            else:
                start = datetime.strptime(start_datetime, "%Y-%m-%d")
        else:
            start = None

        if end_datetime:
            if "T" in end_datetime:
                end = datetime.strptime(end_datetime, "%Y-%m-%dT%H:%M:%S")
            else:
                end = datetime.strptime(end_datetime, "%Y-%m-%d")
        else:
            end = None

    except:
        raise ValueError(
            "Failed to parse {} and {} datetimes!".format(start_datetime, end_datetime)
        )

    return start_datetime, end_datetime


def check_nodata(nodata):
    return nodata


def check_num_workers(num_workers):
    return num_workers


def check_srs(srs):
    try:
        if srs:
            epsg_check = 'EPSG' in srs
            proj_check = 'proj' in srs
            assert(epsg_check or proj_check)
    except:
        print('SRS {} is invalid!'.format(srs))

    return srs


def check_gdal_mem(gdal_mem):
    return gdal_mem


def check_cutline(cutline):
    try:
        if cutline:
            assert(os.path.exists(cutline))
    except:
        raise ValueError('Cutline {} does not exist!'.format(cutline))

    return cutline


def check_gs_bucket(gs_bucket):
    try:
        if gs_bucket:
            assert(gs_bucket.startswith('gs://'))
    except:
        raise ValueError('gs_bucket {} is invalid! must start with gs://'.format(gs_bucket))

    return gs_bucket


def check_remove_local(remove_local):
    return remove_local


def check_verbose(verbose):
    return verbose
