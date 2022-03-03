"""
platform.py

Handy functions that wrap the Descartes Labs platform.

Author: Krishna Karra
"""

import descarteslabs as dl
import os
from subprocess import check_output
from multiprocessing import Pool


def copy_to_gs(tif_file, gs_bucket, remove_local, verbose):
    '''
    copy_to_gs
    '''

    cmd = 'gsutil -q cp {} {}/'.format(tif_file, gs_bucket)
    check_output(cmd.split())

    if verbose:
        print(cmd)

    if remove_local:
        cmd = 'rm {}'.format(tif_file)
        check_output(cmd.split())

        if verbose:
            print(cmd)

    return True


def rasterize_id(i, bands, outdir, verbose):
    '''
    rasterize_id
    '''

    of = os.path.join(outdir, i)
    meta = dl.raster.raster(i,
                            bands=bands,
                            save=True,
                            outfile_basename=of)

    if verbose:
        print('\tRasterized {}'.format(i))

    return True


def rasterize_dltile(dltile, product_id, start_datetime, end_datetime, bands, outdir, verbose):
    '''
    rasterize_dltile
    '''

    dlkey = dltile['properties']['key']
    of = os.path.join(outdir, dlkey)
    ids = dl.metadata.ids(products=[product_id],
                          start_datetime=start_datetime,
                          end_datetime=end_datetime,
                          dltile=dltile,
                          limit=None)

    if not ids:
        return False

    meta = dl.raster.raster(ids,
                            bands=bands,
                            dltile=dltile,
                            save=True,
                            outfile_basename=of)

    if verbose:
        print('Rasterized {}'.format(dlkey))

    return True


def dump_scenes(product_id,
                bands,
                start_datetime,
                end_datetime,
                geometry,
                outdir,
                num_workers,
                verbose):
    '''
    dump_scenes

    Dump raw unmerged GeoTIFFs from a DL product to a directory
    '''

    ids = dl.metadata.ids(products=[product_id],
                          start_datetime=start_datetime,
                          end_datetime=end_datetime,
                          geom=geometry,
                          limit=None)

    if verbose:
        print('Found {} IDs to rasterize'.format(len(ids)))

    if num_workers == 1:
        for i in ids:
            rasterize(i, bands, outdir, verbose)
    else:
        pool = Pool(num_workers)
        raster_args = list()
        for i in ids:
            raster_args.append((i, bands, outdir, verbose))

        pool.starmap(rasterize_id, raster_args)
        pool.close()

    return True


def dump_tiles(product_id,
               bands,
               start_datetime,
               end_datetime,
               geometry,
               resolution,
               tilesize,
               outdir,
               num_workers,
               verbose):
    '''
    dump_tiles

    Dump tiles over a geometry from a DL product to a directory
    '''

    dltile_iter = dl.raster.iter_dltiles_from_shape(resolution=resolution,
                                                    tilesize=tilesize,
                                                    pad=0,
                                                    shape=geometry)

    dltiles = list()
    for i in dltile_iter:
        dltiles.append(i)

    if verbose:
        print('Found {} dltiles to rasterize'.format(len(dltiles)))

    if num_workers == 1:
        for dltile in dltiles:
            rasterize_dltile(dltile, product_id, start_datetime, end_datetime, bands, outdir, verbose)
    else:
        pool = Pool(num_workers)
        raster_args = list()
        for dltile in dltiles:
            raster_args.append((dltile, product_id, start_datetime, end_datetime, bands, outdir, verbose))

        pool.starmap(rasterize_dltile, raster_args)
        pool.close()

    return True
    
