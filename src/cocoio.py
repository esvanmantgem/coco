import errno, sys, os, pathlib
import pandas as pd

SPEC_F = 'spec.dat'
PU_F = 'pu.dat'
PUVSPR_F = 'puvspr.dat'

def process_path(path):
    ''' check if path exists, raise exception otherwise '''
    if os.path.isdir(path):
        return path
    else:
        raise NotADirectoryError(errno.ENOENT, os.strerror(errno.ENOENT), path)

def open_file(path, filename):
    ''' open file if possible, raise exception otherwise '''
    fullpath = os.path.join(path, filename)
    if os.path.isfile(fullpath):
        # Filename is a relative path inside the input folder
        return fullpath
    else:
        if os.path.isfile(filename):
            # Filename is an absolute path
            return filename
        else:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), fullpath)

def read_standard_files(path):
    species = pd.read_csv(open_file(path, SPEC_F))
    pu = pd.read_csv(open_file(path, PU_F))
    puvspr = pd.read_csv(open_file(path, PUVSPR_F))
    return (species, pu, puvspr)

def read_connectivity_data(path, args):
    ''' check connectivity data type and return read file '''
    files = []
    if args.con_matrix:
        for matrix in args.con_matrix:
            files.append(read_connectivity_matrix(open_file(path, matrix)))
    elif args.habitat_edgelist:
        for edgelist in args.habitat_edgelist:
            files.append(pd.read_csv(open_file(path, edgelist)))
    elif args.con_edgelist:
        for edgelist in args.con_edgelist:
            files.append(pd.read_csv(open_file(path, edgelist)))
    return files

def read_connectivity_matrix(file):
    ''' read connectivity matrix '''
    dft = pd.read_csv(file)
    # fix possible unnamed columns in input file
    if dft.columns.str.contains('^Unnamed:').any():
        dft = pd.read_csv(file, index_col=[0])
    dft.columns = dft.columns.astype(int)
    return dft

def save_csv(file, path, name):
    # create output folder if it doesn't exist
    if not os.path.exists(path):
        os.makedirs(path)

    # write solutions to file
    file.to_csv(os.path.join(path,name), index=False)

def print_solution_stats(solution, conservation, timer):
    print("Solver time: ", timer.solver_time())
    print("Total time: ", timer.setup_time())
    print("Objective value:", solution.obj_val)
    print("Total cost: ", solution.total_cost(conservation))
