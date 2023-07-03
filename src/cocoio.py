# Copyright (c) 2022, Eline van Mantgem
#
# This file is part of Coco.
#
# Coco is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Coco is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Coco. If not, see <http://www.gnu.org/licenses/>.

import errno, sys, os, pathlib
from osgeo import gdal
import pandas as pd
import constant as c
import feature_map as fm
import numpy as np
import matplotlib.pyplot as plt
import json

def process_path(path):
    """
    Check if the path exists, raise exception otherwise

    Parameters
    ----------
    path : str
        Path to a folder

    Returns
    -------
    None if ok, NotADirectoryError otherwise
    """

    if os.path.isdir(path):
        return path
    else:
        raise NotADirectoryError(errno.ENOENT, os.strerror(errno.ENOENT), path)

def open_file(path, filename=None):
    """
    Open the file if possible, raise an exception otherwise

    Parameters
    ----------
    path : str
        Path to the folder containing the file
    filename : str
        Name of the file to open

    Returns
    -------
        The full name of the path and filename or an exception if the file is not found
    """

    if filename:
        fullpath = os.path.join(path, filename)
        if '..' in fullpath:
            fullpath = os.path.abspath(fullpath)
    else:
        fullpath = path
    if os.path.isfile(fullpath):
        # Filename is a relative path inside the input folder
        return fullpath
    else:
        if os.path.isfile(filename):
            # Filename is an absolute path
            return filename
        else:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), fullpath)


def read_tif(file):
    ds = gdal.Open(file, gdal.GA_ReadOnly)

    if ds.GetDriver().LongName != 'GeoTIFF':
        error = "Wrong driver, set GeoTIFF"
        sys.exit(error)

    return ds

def get_map(fid, path, file):
    ds = read_tif(open_file(path, file))

    rb = ds.GetRasterBand(1)
    img_array = rb.ReadAsArray()
    pu = img_array.flatten()

    min_val = rb.GetMinimum()
    max_val = rb.GetMaximum()
    no_data = rb.GetNoDataValue()

    if no_data is None:
        no_data = 65535

    x_length = ds.RasterXSize
    y_length = ds.RasterYSize


    geotransform = ds.GetGeoTransform()
    projection = ds.GetProjection()

    fmap = fm.FeatureMap(fid, pu, min_val, max_val, x_length, y_length, geotransform, projection, no_data)
    #write_tif(fmap, 'output')
    return fm.FeatureMap(fid, pu, min_val, max_val, x_length, y_length, geotransform, projection, no_data)

def read_file(file):
    with open(file, 'r') as f:
        return f.read()

def read_config_file(config):
    path = os.path.dirname(config)
    config_f = json.loads(read_file(open_file(config)))

    features = pd.DataFrame.from_dict(config_f["features"], orient="index")
    features['feature'] = features.index
    features = features.reset_index()

    maps = []
    for feature, file in zip(features.index, features['file']):
        maps.append(get_map(feature, path, file))
    return (features, maps, config_f)

def write_tif(fmap, output):
    name = output + '/' + fmap.fid + '.tif'
    driver = gdal.GetDriverByName("GTiff")
    outdata = driver.Create(name, fmap.x_length, fmap.y_length, 1, gdal.GDT_UInt16)
    outdata.SetGeoTransform(fmap.geotransform)
    outdata.SetProjection(fmap.projection)
    arr_out = np.reshape(fmap.pu, (fmap.y_length, fmap.x_length))
    #print(arr_out)
    #arr_out =arr_out * 1000
    outdata.GetRasterBand(1).WriteArray(arr_out)
    #outdata.GetRasterBand(1).SetNoDataValue(10000)##if you want these values transparent
    outdata.GetRasterBand(1).SetNoDataValue(fmap.no_data)##if you want these values transparent
    outdata.FlushCache()
    #show_tif(fmap, arr_out)

def show_fmap(fmap, output=None):
    arr_out = np.reshape(fmap.pu, (fmap.y_length, fmap.x_length))

    f = plt.figure()
    cmap = plt.colormaps['viridis']
    cmap.set_under('white')
    cmap.set_over('white')

    #plt.imshow(img_array, cmap=cmap, vmin=min, vmax=max)
    plt.imshow(arr_out, cmap=cmap, vmin=fmap.min_val, vmax=fmap.max_val)

    print("MAX VAL:", fmap.max_val)

    if output:
        name = output + '/' + fmap.fid + '.png'
    #plt.figure(num='This is the title')
        plt.savefig(name)
    #if show:
    #    plt.show()
    #f = plt.figure()
    #plt.imshow(arr)
    #plt.savefig('Tiff.png')
    #plt.show()

def read_csv_files(path_arg):
    """
    Opens and reads the standard input files in the path directory

    Parameters
    ----------
    path : str
        Path to the folder containing the files

    Returns
    -------
    A tuple of three DataFrames containing the standard input files (features, pu, pvf) or and error if (a) file(s) could not be opened
    """

    path = process_path(path_arg)
    features = pd.read_csv(open_file(path, c.FEAT_F))
    pu = pd.read_csv(open_file(path, c.PU_F))
    pvf = pd.read_csv(open_file(path, c.PVF_F))
    return (path, features, pu, pvf)

def read_connectivity_data(path, args):
    """
    Check connectivity data type, read the file and return dataframes for each dataset in a list

    Parameters
    ----------
    path : str
        Path to the folder containing the files
    args : Argparse namespace
        Contains all passed arguments.

    Returns
    -------
    A list of Pandas DataFrames where each DataFrame contains the information of one file
    """
    files = []
    if args.con_matrix:
        for matrix in args.con_matrix:
            files.append(read_connectivity_matrix(open_file(path, matrix)))
    elif args.feature_edgelist:
        for edgelist in args.feature_edgelist:
            files.append(pd.read_csv(open_file(path, edgelist)))
    elif args.con_edgelist:
        for edgelist in args.con_edgelist:
            files.append(pd.read_csv(open_file(path, edgelist)))
    return files

def read_pu_data(path, file):
    """
    Opens and reads the attribute planning unit file for connectivity

    Parameters
    ----------
    path : str
        Path to the folder containing the file
    file : str
        Name of the file to open

    Returns
    -------
    A DataFrame containing the planning unit attribute information or an error if the file could not be read
    """

    dft = pd.read_csv(open_file(path, file))
    return dft

def read_connectivity_matrix(file):
    """
    Opens and reads the connectivity matrix file

    Parameters
    ----------
    file : str
        Name of the file to open

    Returns
    -------
    A DataFrame containing the data of the connectivity matrix or an error if the file could not be read
    """
    dft = pd.read_csv(file)
    # fix possible unnamed columns in input file
    if dft.columns.str.contains('^Unnamed:').any():
        dft = pd.read_csv(file, index_col=[0])
    dft.columns = dft.columns.astype(int)
    return dft

def save_csv(df, path, name):
    """
    Saves the dataframe to a csv file and stores it in path

    Parameters
    ----------
    df : Pandas DataFrame
        DataFrame to save
    path : str
        Path to the output folder to store the csv file
    name : str
        Name of the saved csv file

    Returns
    -------
    None
    """

    # create output folder if it doesn't exist
    if not os.path.exists(path):
        os.makedirs(path)

    # write solutions to file
    df.to_csv(os.path.join(path,name), index=False)

def print_solution_stats(solution, conservation, timer):
    """
    Print to console some basic stats on the solution found

    Parameters
    ----------
    solution : Pandas DataFrame
        A Solution Area object containing the information to print
    conservation : Conservation
        A Conservation object containing the information to print
    timer : Timer
        Timer used in the current run
    Returns
    -------
    None
    """

    print("Solver time: ", timer.solver_time())
    print("Total time: ", timer.setup_time())
    print("Objective value:", solution.obj_val)
    print("Total cost: ", solution.total_cost(conservation))
