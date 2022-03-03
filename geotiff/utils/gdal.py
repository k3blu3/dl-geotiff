"""
gdal.py

Wrap a bunch of GDAL command line functions in Python

Author: Krishna Karra
"""

import os
from subprocess import check_output


def reproject_resample(tif_file, 
                       nodata, 
                       cutline, 
                       resolution, 
                       resample, 
                       srs,
                       num_workers,
                       gdal_mem,
                       verbose):
    '''
    reproject_resample

    Re-project and/or resample and/or cutline merged GeoTIFF
    '''
    
    cmd = 'gdalwarp -co COMPRESS=LZW -co BIGTIFF=YES -srcnodata {} -dstalpha'.format(nodata)
    
    if cutline:
        cmd += ' -cutline {} -crop_to_cutline'.format(cutline)
    if resolution:
        cmd += ' -tr {} {} -r {}'.format(resolution, resolution, resample)
    if srs:
        cmd += ' -t_srs "{}"'.format(srs)
    if num_workers > 1:
        cmd += ' -multi -wo NUM_THREADS={}'.format(num_workers)
    if gdal_mem:
        cmd += ' --config GDAL_CACHEMAX {} -wm {}'.format(gdal_mem, gdal_mem)

    tif_out = tif_file.strip('.tif') + '_warp.tif'
    cmd += ' {} {}'.format(tif_file, tif_out)

    #check_output(cmd.split())
    os.system(cmd)

    if verbose:
        print(cmd)

    # remove old file, rename new file to old file
    cmd = 'rm {}'.format(tif_file)
    check_output(cmd.split())
    if verbose:
        print(cmd)

    cmd = 'mv {} {}'.format(tif_out, tif_file)
    check_output(cmd.split())
    if verbose:
        print(cmd)
    
    return True


def merge_tifs(input_dir, tif_file, verbose):
    '''
    merge_tifs

    Merge GeoTIFFs
    '''

    mosaic_file = os.path.join(input_dir, 'mosaic.vrt')
    cmd = 'gdal_translate -co COMPRESS=LZW -co BIGTIFF=YES {} {}'.format(mosaic_file,
                                                                         tif_file)
    check_output(cmd.split())

    if verbose:
        print(cmd)

    return True



def build_mosaic(input_dir, nodata, verbose):
    '''
    build_mosaic

    Build vrt file for gdal_merge
    '''

    input_file_list = os.path.join(input_dir, 'files.txt')
    mosaic_file = os.path.join(input_dir, 'mosaic.vrt')
    cmd = 'gdalbuildvrt -srcnodata {} -input_file_list {} {}'.format(nodata,
                                                                     input_file_list,
                                                                     mosaic_file)
    check_output(cmd.split())
    
    if verbose:
        print(cmd)

    return True


def project_wgs(input_dir, verbose):
    '''
    project_wgs

    Re-project GeoTIFFs in a directory to WGS84
    This removes the old files
    '''

    tif_files = os.listdir(input_dir)
    txt_file = os.path.join(input_dir, 'files.txt')
    of = open(txt_file, 'w')

    for tif_file in tif_files:
        if tif_file.endswith('tif'):
            infile = os.path.join(input_dir, tif_file)
            outfile = os.path.join(input_dir, tif_file.strip('.tif') + '_wgs.tif')

            cmd = 'gdalwarp -r cubic -t_srs EPSG:4326 -co COMPRESS=LZW {} {}'.format(infile, outfile)
            
            try:
                check_output(cmd.split())
                if verbose:
                    print('\t{}'.format(cmd))

                    of.write(outfile + '\n')
            except:
                print('{} failed!'.format(cmd))
            
            os.remove(infile)

    of.close()
    return True
