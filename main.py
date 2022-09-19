import gurobipy as gp
import numpy as np
import pandas as pd
import networkx as nx
import argparse as ap
import matplotlib.pyplot as plt
import pathlib, os, errno, sys
from gurobipy import GRB
from connectivity import *
from conservation import *
from connectivity_metric import *

def parse_args():
    parser = ap.ArgumentParser(description = "Cocoplan command line arguments.")
    parser.add_argument('-path', type=pathlib.Path, help='Folder containing the input files')
    #parser.add_argument('-metric-weight', type=float, help='Weight of the metric in objective function')
    parser.add_argument('-time-limit', type=int, help='Time limit to restrict the runtime of Gurobi')
    parser.add_argument('-strategy', choices=['cf', 'sd', 'opt', 'live-opt'], help='Strategy to calculate the metric')
    parser.add_argument('-metric', choices=['indegree', 'outdegree', 'betcent'], help='Which connectivity metric to use')
    parser.add_argument('-mc', action='store_true', help='Which connectivity metric to use')
    min_value_parser = parser.add_mutually_exclusive_group()
    min_value_parser.add_argument('-metric-min', type=float, help='Minimum value to use when discritzing metric')
    min_value_parser.add_argument('-metric-min-type', choices=['min', 'mean', 'median'], help='Minimum value to calculate when discritzing metric')
    max_value_parser = parser.add_mutually_exclusive_group()
    max_value_parser.add_argument('-metric-max', type=float, help='Maximum value to use when discritzing metric')
    max_value_parser.add_argument('-metric-max-type', choices=['max', 'mean', 'median'], help='Minimum value to calculate when discritzing metric')
    #parser.add_argument('-metric-max', type=float, help='Maximum value to use when discritzing metric')
    metric_parser = parser.add_mutually_exclusive_group(required=True)
    metric_parser.add_argument('-metric-prop', type=float, help='minimal proportion of the total metric value to obtain')
    metric_parser.add_argument('-metric-target',type=float, help='minimal target of the metric to obtain')
    #metric_parser.add_argument('--cf', choices=['indegree', 'outdegree', 'betcent'])
    #metric_parser.add_argument('--sd', choices=['indegree', 'outdegree', 'betcent'])
    con_data_parser = parser.add_mutually_exclusive_group(required=True)
    con_data_parser.add_argument('-con-matrix', type=str, help='File containing the connectivity matrix')
    con_data_parser.add_argument('-con-edgelist', type=str, help='File containing the connectivity edgelist')
    return parser.parse_args()

def process_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise NotADirectoryError(errno.ENOENT, os.strerror(errno.ENOENT), path)

def open_file(path, filename):
    if os.path.isfile(path / filename):
        return path / filename
    else:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path / filename)

def read_connectivity_matrix(file):
    dft = pd.read_csv(file)
    if dft.columns.str.contains('^Unnamed:').any():
        dft = pd.read_csv(file, index_col=[0])
    dft.columns = dft.columns.astype(int)
    return dft

def show_solution(m, pux, conservation):
    pu = conservation.pu
    pu_val = []
    for p, x in zip(pux['pu'], pux['x']):
        #print(x.getAttr('Xn'))
        pu_val.append(1) if x.getAttr('Xn') >= 1 else pu_val.append(0)
    pu['pu_val'] = pu_val
    ax1 = pu.plot.scatter(x='xloc', y='yloc', c='pu_val', colormap='viridis')
    plt.show()

def print_solution(m, pux, conservation):
    pu = conservation.pu
    pu_val = []
    for p, x in zip(pux['pu'], pux['x']):
        #print(x.getAttr('Xn'))
        pu_val.append(1) if x.getAttr('Xn') >= 1 else pu_val.append(0)
    pu['pu_val'] = pu_val
    #print(pu)
    pu.to_csv('solution.csv', index=False)

def init_connectivity(args, con_data):
    metric_weight = args.metric_prop if args.metric_target == None else args.metric_target
    metric_target = False if args.metric_target == None else True
    #return Connectivity(args.metric, args.strategy, metric_weight, metric_target, metric_min, args.metric_max, args.mc, con_data)
    connectivity = Connectivity(args.strategy, metric_weight, metric_target, con_data)
    connectivity.add_metric(args.metric)
    print_metric_values(connectivity.get_metric(args.metric))

    if args.metric_min_type is not None:
        connectivity.drop_smaller_type(args.metric, args.metric_min_type)
    if args.metric_max_type is not None:
        connectivity.drop_greater_type(args.metric, args.metric_min)

    if args.metric_min is not None:
        connectivity.drop_smaller_value(args.metric, args.metric_min)
    if args.metric_max is not None:
        connectivity.drop_greater_value(args.metric, args.metric_min)
    if args.mc:
        connectivity.set_values_to_one(args.metric)
    return connectivity

def print_metric_values(metric):
    #metric_values.to_csv('met_val.csv', index=False)
    print()
    print("Sum of metric value: ", metric.sum)
    print("Mean of metric value: ", metric.mean)
    print("Median of metric value: ", metric.median)
    print("Min of metric value: ", metric.min)
    print("Max of metric value: ", metric.max)

def init_pux(m, pu):
    x = [None] * len(pu)
    for i in range(len(x)):
        x[i] = m.addVar(vtype=GRB.BINARY, name = "x_" + str(pu[i]))

    data = { "pu": pu, "x": x }
    m.update()
    return pd.DataFrame(data)

# Enforce the total amount of the metric k over all selected pu's x is >= to proportion t of the total (tk)
# sum(rik * xi) >= tk for all pu i, for all pu k
def c_set_metric_target(m, conservation, pux, connectivity):
        for metric_name in connectivity.metrics:
            xi = []
            rik = []

            metric_values = connectivity.get_metric_values(metric_name)
            #print_metric_values(metric_values)
            total = metric_values['value'].sum()

            # If proportion instead of target
            tk = connectivity.weight * total if not connectivity.target else connectivity.weight
            print("Target to reach for connectivity: ", tk, "\n")
            for pu, value in zip(metric_values['pu'], metric_values['value']):
                x_pu = pux[pux['pu'] == pu]
                xi.append(x_pu['x'].item())
                rik.append(value)
            # add constraint for species k
            m.addConstr(sum(xi[i] * rik[i] for i in range(len(xi))) >= tk)
        m.update()

# Enforce the covered amount of species k is >= to the target or proportion of species k (tk)
# sum(rik * xi) >= tk for all pu i, for all species k
def c_set_species_target(m, conservation, pux):
    # group puvspr in slices based on species_id giving all pu's for each species
    species = conservation.species

    pu_per_sp = [y for x, y in conservation.puvspr.groupby('species')]
    if 'prop' in species.columns:
    #if not connectivity.target:
        amounts = conservation.puvspr.groupby(["species"]).amount.sum().reset_index()
    for sp in pu_per_sp:
        # select species id from last row (index not possible)
        k = sp['species'].iloc[-1]
        if 'target' in species.columns:
            # tk = value of target in row with species id
            tk = species.loc[species['id'] == k, 'target'].item()
        elif 'prop' in species.columns:
            prop = species.loc[species['id'] == k, 'prop'].item()
            amount = amounts.loc[amounts['species'] == k, 'amount'].item()
            tk = prop * amount
        else: #TODO move this check, ugly here
            error = "Error: target or prop required in species.dat"
            sys.exit(error)

        # add x_i * r_ik
        xi = []
        rik = []
        for pu, amount in zip(sp['pu'], sp['amount']):
            x_pu = pux[pux['pu'] == pu]
            xi.append(x_pu['x'].item())
            rik.append(amount)
        # add constraint for species k
        m.addConstr(sum(xi[i] * rik[i] for i in range(len(xi))) >= tk)
        m.update()

#def calculate_metric_values(g, metric):
#    if metric == None: #solution metrics not implemented yet
#        error = "Error: solution metrics not implemented yet"
#        sys.exit(error)
#    else:
#        return ConnectivityMetric().get_connectivity_metrics(g, metric)

# TODO rewrite
def set_metric_objective(m, conservation, pux, connectivity):
    pu = conservation.pu
    pu_c = []
    pu_x = []
    pu_m = []
    #metric_values = connectivity.get_connectivity_metrics(pu)
    # only one metric allowed, so list is size 1
    metric_values = connectivity.get_metric_values(list(connectivity.metrics.keys())[0])
    for pu_id, pu_cost in zip(pu['id'], pu['cost']):
        pu_c.append(pu_cost)
        pu_x.append(pux.loc[pux['pu'] == pu_id, 'x'].item())
        if pu_id in metric_values['pu'].values:
            pu_m.append(metric_values.loc[metric_values['pu'] == pu_id, 'value'].item())
        else:
            pu_m.append(0)

    # set objective: minimize sum(ci * xi for all pu i) + sum(x_i * -in_degree)
    m.setObjective(sum(pu_x[i] * pu_c[i] for i in range(len(pu_c))) - con_met.weight * sum(pu_x[j] * pu_m[j] for j in range(len(pu_m))), GRB.MINIMIZE)
    m.update()

# min ci xi
def set_objective(m, conservation, pux, connectivity):
    # cost objective: select all ci and xi
    pu = conservation.pu
    if connectivity.strategy == 'opt':
        set_metric_objective(m, conservation, pux, connectivity)
    else:
        pu_c = []
        pu_x = []
        #metric_values = connectivity.get_connectivity_metrics(pu)
        for pu_id, pu_cost in zip(pu['id'], pu['cost']):
            pu_c.append(pu_cost)
            pu_x.append(pux.loc[pux['pu'] == pu_id, 'x'].item())

        # set objective: minimize sum(ci * xi for all pu i) + sum(x_i * -in_degree)
        m.setObjective(sum(pu_x[i] * pu_c[i] for i in range(len(pu_c))), GRB.MINIMIZE)
        m.update()

def main():
    # parse args
    args = parse_args()
    path = process_path(args.path)

    # create datastructures
    species = pd.read_csv(open_file(path, 'spec.dat'))
    pu = pd.read_csv(open_file(path, 'pu.dat'))
    puvspr = pd.read_csv(open_file(path, 'puvspr.dat'))
    bounds = pd.read_csv(open_file(path, 'bound.dat'))
    #con_data = pd.read_csv(open_file(path, args.connectivity_data))
    con_input = args.con_matrix if args.con_edgelist == None else args.con_edgelist
    con_data = read_connectivity_matrix(open_file(path, con_input))

    conservation = Conservation(pu, species, puvspr, bounds)
    connectivity = init_connectivity(args, con_data)

    #g = nx.from_pandas_adjacency(con_data, create_using=nx.DiGraph())
    #g = nx.from_pandas_edgelist(bounds, 'id1', 'id2', 'boundary', create_using=nx.DiGraph())

    #nx.draw(g, with_labels = True)
    #plt.show()

    # create model
    m = gp.Model("Coco")
    pux = init_pux(m, conservation.pu["id"])
    c_set_species_target(m, conservation, pux)
    if connectivity.strategy == 'cf':
        c_set_metric_target(m, conservation, pux, connectivity)
    set_objective(m, conservation, pux, connectivity)


    if args.time_limit:
        m.setParam('TimeLimit', args.time_limit)
    m.optimize()

    # show output
    show_solution(m, pux, conservation)
    print_solution(m, pux, conservation)

if __name__ == '__main__':
    main()
