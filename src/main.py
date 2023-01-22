import gurobipy as gp
import pandas as pd
import cocoio as cio
import cocoparser as cparser
import timer as ctimer
import connectivity as conn
import conservation as cons
import solution as sol
import sys
from gurobipy import GRB

# HPC: uncomment next 3 lines and and uncomment print_stats function call
#import sys
#sys.path.append("../analysis")
#from gb_output import print_stats

###                                        ###
# Analysis and output functions              #
###                                        ###

def process_solution(m, conservation, timer, pux):
    # LP
    #lp = True
    #if lp:
    #    return process_lp_relaxation(m, conservation, timer, pux)
    #else:
    ''' setup basic solution from model '''
    pu = conservation.pu
    pu_val = []
    pu_id = []
    xloc = []
    yloc = []
    for p, x in zip(pux['pu'], pux['x']):
        pu_id.append(p)
        pu_val.append(1) if x.getAttr('Xn') >= 1 else pu_val.append(0)
        xloc.append(pu.loc[pu['id'] == p, 'xloc'].item())
        yloc.append(pu.loc[pu['id'] == p, 'yloc'].item())
    df = pd.DataFrame(list(zip(pu_id, pu_val, xloc, yloc)), columns = ['pu', 'x', 'xloc', 'yloc'])
    obj_val = m.getObjective().getValue()
    return sol.SolutionArea(df, obj_val, m.MIPGap, timer)

def process_lp_relaxation(m, conservation, timer, pux):
    pu = conservation.pu
    pu_val = []
    pu_id = []
    xloc = []
    yloc = []
    for p, x in zip(pux['pu'], pux['x']):
        pu_id.append(p)
        pu_val.append(x.X)
        xloc.append(pu.loc[pu['id'] == p, 'xloc'].item())
        yloc.append(pu.loc[pu['id'] == p, 'yloc'].item())
    df = pd.DataFrame(list(zip(pu_id, pu_val, xloc, yloc)), columns = ['pu', 'x', 'xloc', 'yloc'])
    obj_val = m.getObjective().getValue()
    return sol.SolutionArea(df, obj_val, None, timer)

def get_args_stats(args):
    arg_names = []
    arg_values = []
    for arg in vars(args):
        arg_names.append(arg)
        arg_values.append(getattr(args, arg))
    return pd.DataFrame(list(zip(arg_names, arg_values)), columns = ['name', 'value'])

def analyze_and_save_solution(args, conservation, solution, connectivity=None):
    ''' plot and show a solution map and write solution to 'solution.csv' '''
    path = args.output

    # analyze solution
    spec_sum = solution.species_sum(conservation)
    #print(spec_sum)
    run_stats = solution.save_run_stats(conservation)
    #print(run_stats)
    arg_stats = get_args_stats(args)
    #print(arg_stats)
    arg_run_stats = pd.concat([run_stats, arg_stats])
    #print(arg_run_stats)

    if connectivity:
        metric_sum = solution.metrics_sum(connectivity)
        print(metric_sum)
        cio.save_csv(metric_sum, path, 'metrics.csv')

    # save csv files
    cio.save_csv(spec_sum, path, 'targets.csv')
    cio.save_csv(solution.pux, path, 'solution.csv')
    cio.save_csv(arg_run_stats, path, 'runstats.csv')

    solution.show_map(path)

###                                        ###
# Initializing conservation and connectivity #
###                                        ###

def process_metric_threshold_values(args, connectivity):
    ''' remove values below given min threshold and values above given max threshold '''
    if args.metric_min_type:
        for metric, min_t in zip(args.metric, args.metric_min_type):
            connectivity.drop_smaller_type(metric, min_t)
    elif args.metric_min:
        for metric, min_t in zip(args.metric, args.metric_min):
            connectivity.drop_smaller_value(metric, min_t)
    if args.metric_max_type:
        for metric, max_t in zip(args.metric, args.metric_max_type):
            connectivity.drop_greater_type(metric, max_t)
    elif args.metric_max:
        for metric, max_t in zip(args.metric, args.metric_max_type):
            connectivity.drop_greater_value(metric, max_t)

#def set_metrics(args, connectivity):
#    for metric in args.metric:
#        print("for metric: ", metric)
#        connectivity.set_metric(metric)
#    process_metric_threshold_values(args, connectivity)
#
#    # set all values to 1 if MC flag is set
#    if args.mc:
#        for metric in args.metric:
#            connectivity.set_values_to_one(metric)

def set_connectivity_data(args, con_data, connectivity, pu_data=None):
    if args.con_matrix:
        for i in range(len(con_data)):
            connectivity.set_connectivity_matrix(con_data[i], i, args.metric, pu_data)
    elif args.con_edgelist:
        for i in range(len(con_data)):
            connectivity.set_connectivity_edgelist(con_data[i], i, args.metric, pu_data)
    elif args.habitat_edgelist:
        for data in con_data:
            connectivity.set_habitat_connectivity_edgelist(data, args.metric, pu_data)
    else:
        error = "Please give connectivity input file"
        sys.exit(error)
    #if args.pu_data:
        #for data in pu_data:
    #    connectivity.set_pu_data(pu_data)
    process_metric_threshold_values(args, connectivity)

def init_pre_connectivity(args, con_data, pu_data=None):
    ''' initialize connectivity for the conservation feature approach '''
    # set metric weight and bool target or prop as given by params
    if args.strategy == 'cf':
        metric_weight = args.metric_prop if args.metric_target == None else args.metric_target
        metric_target = False if args.metric_target == None else True
    elif args.strategy == 'cost-con':
        metric_weight = args.metric_weight
        metric_target = False
    elif args.strategy == 'con' or args.strategy == 'con-blm':
        metric_weight = None
        metric_target = False

    # create new connectivity object, add all data and metrics.
    connectivity = conn.Connectivity(args.strategy, metric_weight, args.complete_graph, metric_target)
    if args.strategy == 'cost-con' and args.cost_weight:
        connectivity.cost_weight = args.cost_weight
    set_connectivity_data(args, con_data, connectivity, pu_data)
    #set_metrics(args, connectivity)
    return connectivity

def init_connectivity(args, path):
    ''' initialize connectivity data '''
    con_data = cio.read_connectivity_data(path, args)
    pu_data = cio.read_pu_data(path, args.pu_data) if args.pu_data else None
    if args.strategy == 'cf' or args.strategy == 'cost-con' or args.strategy == 'con' or args.strategy == 'con-blm':
        return init_pre_connectivity(args, con_data, pu_data)
    #elif args.strategy == 'opt-live':
    #    error = "Live optimization of metric not implemented yet"
    #    exit(error)
    else:
        error = "Unknown strategy"
        exit(error)

def init_bounds(args, path):
    file = args.habitat_edgelist[0] if args.strategy == 'sd' else 'bound.dat'
    bounds = pd.read_csv(cio.open_file(path, file))

    if args.strategy == 'sd':
        bounds = bounds.loc[bounds['value'] != 0].reset_index(drop=True)
        conservation.bounds = bounds.rename(columns={'value': 'boundary'})
    return bounds

def init_conservation(args, pu, species, puvspr, bounds):
    conservation = cons.Conservation(pu, species, puvspr, bounds)
    if args.strategy == 'con' or args.strategy == 'con-blm':
        conservation.max_cost = args.max_cost
        conservation.min_cost = args.min_cost if args.min_cost else None
    return conservation

def init_conservation_and_connectivity(args, path, species, pu, puvspr):
    bounds = init_bounds(args, path) if args.blm else None
    conservation = init_conservation(args, pu, species, puvspr, bounds)
    connectivity = init_connectivity(args, path) if args.strategy != 'cost' else None
    return (conservation, connectivity)

###                                        ###
# Constraints related functions              #
###                                        ###

def set_target_ge_constraint(m, pux, pu_ids, pu_values, tk):
    '''
    enforce the total amount of pu_values k over all selected x's  of pu_ids i >= tk
    sum(rik * xi) >= tk for all pu_ids i, for all metrics k
    '''
    xi = []
    rik = []

    # select x of pu i and the amount of metric k in pu i
    for pu, value in zip(pu_ids, pu_values):
        x_pu = pux[pux['pu'] == pu]
        xi.append(x_pu['x'].item())
        rik.append(value)
    # add contraint to enforce the total amount of metric k in selected pu i's >= the target (or prop) of metric k
    m.addConstr(sum(xi[i] * rik[i] for i in range(len(xi))) >= tk)
    m.update()

def set_target_le_constraint(m, pux, pu_ids, pu_values, tk):
    '''
    enforce the total amount of pu_values k over all selected x's  of pu_ids i >= tk
    sum(rik * xi) <= tk for all pu_ids i, for all metrics k
    '''
    xi = []
    rik = []

    # select x of pu i and the amount of metric k in pu i
    for pu, value in zip(pu_ids, pu_values):
        x_pu = pux[pux['pu'] == pu]
        xi.append(x_pu['x'].item())
        rik.append(value)
    # add contraint to enforce the total amount of metric k in selected pu i's >= the target (or prop) of metric k
    m.addConstr(sum(xi[i] * rik[i] for i in range(len(xi))) <= tk)
    m.update()

def c_set_metric_target(m, conservation, connectivity, pux):
    for metric in connectivity.metrics:
        if metric == 'betcent' or metric == 'indegree' or metric == 'outdegree':
            c_set_node_metric_target(m, conservation, connectivity, pux, metric)
        elif metric == 'ec':
            c_set_edge_metric_target(m, conservation, connectivity, pux, metric)
    m.update()

def c_set_node_metric_target(m, conservation, connectivity, pux, metric_k):
    '''
    set target constraints for each metric
    sum(rik * xi) >= tk for all pu i, for all metrics k
    '''
    for condata in connectivity.get_connectivity_data():
        metric_values = condata.get_metric_values(metric_k)
        total = metric_values['value'].sum()

        # calculate tk based on proportion or target
        tk = connectivity.weight * total if not connectivity.target else connectivity.weight
        condata.get_metric(metric_k).set_target(tk)
        set_target_ge_constraint(m, pux, metric_values['pu'], metric_values['value'], tk)
    m.update()

def c_set_edge_metric_target(m, conservation, connectivity, pux, metric_k):
    '''
    set target constraints for each metric
    sum(rik * xi) >= tk for all pu i, for all metrics k
    '''
    for condata in connectivity.get_connectivity_data():
        #print(condata)
        pu_z = []
        pu_m = []
        metric_values = condata.get_metric_values(metric_k)
        #print(metric_values)
        total = metric_values['value'].sum()

        for pu1, pu2, val in zip(metric_values['pu1'], metric_values['pu2'], metric_values['value']):
            x_i = pux.loc[pux['pu'] == pu1, 'x'].item()
            x_j = pux.loc[pux['pu'] == pu2, 'x'].item()
            z = m.addVar(vtype=GRB.BINARY, name = "z_" + str(x_i) + "_" + str(x_j))
            m.addConstr(z == gp.and_([x_i, x_j]))
            pu_z.append(z)
            pu_m.append(val)

        # calculate tk based on proportion or target
        tk = connectivity.weight * total if not connectivity.target else connectivity.weight
        condata.get_metric(metric_k).set_target(tk)


        #print("---------------------------------add constr")
        m.addConstr(sum(pu_z[i] * pu_m[i] for i in range(len(pu_z))) >= tk)
        #set_target_ge_constraint(m, pux, metric_values['pu'], metric_values['value'], tk)

    m.update()
#def c_set_metric_target(m, conservation, connectivity, pux):
#    '''
#    set target constraints for each metric
#    sum(rik * xi) >= tk for all pu i, for all metrics k
#    '''
#    for condata in connectivity.get_connectivity_data():
#        for metric_k in condata.metrics:
#            # for each metric, set the target constraints
#            metric_values = condata.get_metric_values(metric_k)
#            total = metric_values['value'].sum()
#
#            # calculate tk based on proportion or target
#            tk = connectivity.weight * total if not connectivity.target else connectivity.weight
#            condata.get_metric(metric_k).set_target(tk)
#            set_target_ge_constraint(m, pux, metric_values['pu'], metric_values['value'], tk)
#        m.update()
#
def c_set_cost_target(m, conservation, pux):
    # setting a max cost is mandatory for this strategy
    set_target_le_constraint(m, pux, conservation.pu['id'], conservation.pu['cost'], conservation.max_cost)
    if conservation.min_cost:
        set_target_ge_constraint(m, pux, conservation.pu['id'], conservation.pu['cost'], conservation.min_cost)

def c_set_species_target(m, conservation, pux):
    ''' set target constraints for each species
        sum(rik * xi) >= tk for all pu i, for all species k
    '''
    # group puvspr in slices based on species_id giving all pu's for each species
    pu_per_sp = [y for x, y in conservation.puvspr.groupby('species')]
    for sp in pu_per_sp:
        # select species id from last row (index not possible)
        k = sp['species'].iloc[-1]
        tk = conservation.get_target(k)
        set_target_ge_constraint(m, pux, sp['pu'], sp['amount'], tk)
        m.update()

###                                        ###
# Objective related functions                #
###                                        ###

def get_cost_and_selected_pu(m, conservation, pux):
    pu_c = []
    pu_x = []
    # cost objective: select all ci and xi
    for pu_id, pu_cost in zip(conservation.pu['id'], conservation.pu['cost']):
        pu_c.append(pu_cost)
        pu_x.append(pux.loc[pux['pu'] == pu_id, 'x'].item())
    return (pu_c, pu_x)

#def set_cost_metric_objective(m, conservation, connectivity, pux):
#    pu = conservation.pu
#    pu_m = []
#    pu_mx = []
#
#    (pu_c, pu_x) = get_cost_and_selected_pu(m, conservation, pux)
#
#    #data_set = []
#    for condata in connectivity.get_connectivity_data():
#        metric_values = []
#        for metric_k in condata.metrics:
#            # TODO add option to NOT normalize data?
#            metric_values = condata.get_normalized_metric_values(metric_k).copy()
#
#            for pu_id, pu_cost in zip(pu['id'], pu['cost']):
#                if pu_id in metric_values['pu'].values:
#                    pu_m.append(metric_values.loc[metric_values['pu'] == pu_id, 'value'].item())
#                    pu_mx.append(pux.loc[pux['pu'] == pu_id, 'x'].item())
#
#    # set objective: minimize sum(ci * xi for all pu i) + sum(x_i * -in_degree)
#    m.setObjective(sum(pu_x[i] * pu_c[i] for i in range(len(pu_c))) -
#                   connectivity.weight *
#                   sum(pu_mx[j] * pu_m[j] for j in range(len(pu_m))), GRB.MINIMIZE)
#    m.update()

def normalize_node(metric_values):
    print("node: min = ", metric_values['value'].min(), " max = ", metric_values['value'].max())
    if metric_values['value'].min() != metric_values['value'].max():
        norm_data = (metric_values['value'] - metric_values['value'].min())/(metric_values['value'].max() - metric_values['value'].min())
        return pd.DataFrame(list(zip(metric_values['pu'], norm_data)), columns = ['pu', 'value'])
    else:
        # TODO: all values are the same, assume they are normalized (otherwise div by 0 error)
        print("node metric min == max")
        return metric_values

def normalize_edge(metric_values):
    print("edge: min = ", metric_values['value'].min(), " max = ", metric_values['value'].max())
    if metric_values['value'].min() != metric_values['value'].max():
        norm_data = (metric_values['value'] - metric_values['value'].min())/(metric_values['value'].max() - metric_values['value'].min())
        return pd.DataFrame(list(zip(metric_values['pu1'], metric_values['pu2'], norm_data)), columns = ['pu1',  'pu2', 'value'])
    else:
        # TODO: all values are the same, assume they are normalized (otherwise div by 0 error)
        print("edge metric min == max")
        return metrics_values

def set_node_cost_metric_objective(m, conservation, connectivity, pux, metric, pu_mx, pu_m):
    pu = conservation.pu
    #pu_m = []
    #pu_mx = []

    #(pu_c, pu_x) = get_cost_and_selected_pu(m, conservation, pux)

    values_sum = pd.DataFrame(columns = ['pu', 'value'])
    for condata in connectivity.get_connectivity_data():
        print("setting metric node objective: ", metric)
        metric_values = condata.get_metric_values(metric).copy()
        values_sum = pd.concat([values_sum, metric_values], ignore_index=True)
    values_sum = normalize_node(values_sum.groupby(['pu']).value.sum().reset_index())

    for pu_id, pu_cost in zip(pu['id'], pu['cost']):
        if pu_id in values_sum['pu'].values:
            pu_m.append(values_sum.loc[values_sum['pu'] == pu_id, 'value'].item())
            pu_mx.append(pux.loc[pux['pu'] == pu_id, 'x'].item())

    return (pu_mx, pu_m)
    # set objective: minimize sum(ci * xi for all pu i) + sum(x_i * -in_degree)
    #m.setObjective((connectivity.cost_weight * sum(pu_x[i] * pu_c[i] for i in range(len(pu_c)))) -
    #               connectivity.weight *
    #               sum(pu_mx[j] * pu_m[j] for j in range(len(pu_m))), GRB.MINIMIZE)

def set_edge_cost_metric_objective(m, conservation, connectivity, pux, metric, pu_z, pu_m):
    pu = conservation.pu
    #pu_m = []
    #pu_z = []

    #(pu_c, pu_x) = get_cost_and_selected_pu(m, conservation, pux)

    values_sum = pd.DataFrame(columns = ['pu1',  'pu2', 'value'])
    for condata in connectivity.get_connectivity_data():
        print("setting metric edge objective: ", metric)
        metric_values = condata.get_metric_values(metric).copy()
        #print(metric_values)
        values_sum = pd.concat([values_sum, metric_values], ignore_index=True)
    values_sum = normalize_edge(values_sum.groupby(['pu1', 'pu2']).value.sum().reset_index())
    #values_sum = values_sum.groupby(['pu1', 'pu2']).value.sum().reset_index()

    for pu1, pu2, val in zip(values_sum['pu1'], values_sum['pu2'], values_sum['value']):
        x_i = pux.loc[pux['pu'] == pu1, 'x'].item()
        x_j = pux.loc[pux['pu'] == pu2, 'x'].item()
        z = m.addVar(vtype=GRB.BINARY, name = "z_" + str(x_i) + "_" + str(x_j))
        m.addConstr(z == gp.and_([x_i, x_j]))
        pu_z.append(z)
        pu_m.append(val)

    return (pu_z, pu_m)

    #m.setObjective((connectivity.cost_weight * sum(pu_x[i] * pu_c[i] for i in range(len(pu_c)))) -
    #               connectivity.weight *
    #               sum(pu_z[j] * pu_m[j] for j in range(len(pu_z))), GRB.MINIMIZE)
    #m.setObjective(sum(pu_x[i] * pu_c[i] for i in range(len(pu_c))) -
    #               connectivity.weight *
    #               sum(pu_z[j] * pu_m[j] for j in range(len(pu_z))), GRB.MINIMIZE)

    #nodes = [y for x, y in values_sum.groupby('pu1')]
    #count = 1
    #for i in nodes:
    #    edges = pd.DataFrame(i).reset_index(drop=True)
    #    print("node: ", count)
    #    for k in range(len(edges)):
            #x_i = pux.loc[pux['pu'] == edges['pu1'][k], 'x'].item()
            #x_j = pux.loc[pux['pu'] == edges['pu2'][k], 'x'].item()
            #z = m.addVar(vtype=GRB.BINARY, name = "z_" + str(x_i) + "_" + str(x_j))
            #m.addConstr(z == gp.and_([x_i, x_j]))
            #pu_z.append(z)
            #pu_m.append(edges['value'][k])
            #print(neighbors['pu1'][k], neighbors['pu2'][k], neighbors['value'][k])


    # set objective: minimize sum(ci * xi for all pu i) + sum(x_i * -in_degree)
    #m.setObjective(sum(pu_x[i] * pu_c[i] for i in range(len(pu_c))) -
    #               connectivity.weight *
    #               sum(pu_z[j] * pu_m[j] for j in range(len(pu_z))), GRB.MINIMIZE)

def set_cost_metric_objective(m, conservation, connectivity, pux):
    (pu_c, pu_x) = get_cost_and_selected_pu(m, conservation, pux)
    dec_vars = []
    dec_values = []

    for metric in connectivity.metrics:
        print("------------------------------------------- metric", metric)
        if metric == 'betcent' or metric == 'indegree' or metric == 'outdegree':
            (dec_vars, dec_values) = set_node_cost_metric_objective(m, conservation, connectivity, pux, metric, dec_vars, dec_values)
        elif metric == 'ec':
            (dec_vars, dec_values) = set_edge_cost_metric_objective(m, conservation, connectivity, pux, metric, dec_vars, dec_values)

    m.setObjective((connectivity.cost_weight * sum(pu_x[i] * pu_c[i] for i in range(len(pu_c)))) -
                   connectivity.weight *
                   sum(dec_vars[j] * dec_values[j] for j in range(len(dec_vars))), GRB.MINIMIZE)
    m.update()

def set_connectivity_objective(m, conservation, connectivity, pux):
    (pu_c, pu_x) = get_cost_and_selected_pu(m, conservation, pux)
    dec_vars = []
    dec_values = []

    for metric in connectivity.metrics:
        print("------------------------------------------- metric", metric)
        if metric == 'betcent' or metric == 'indegree' or metric == 'outdegree':
            (dec_vars, dec_values) = set_node_connectivity_objective(m, conservation, connectivity, pux, metric, dec_vars, dec_values)
        elif metric == 'ec':
            (dec_vars, dec_values) = set_edge_connectivity_objective(m, conservation, connectivity, pux, metric, dec_vars, dec_values)

    m.setObjective(sum(dec_vars[j] * dec_values[j] for j in range(len(dec_vars))), GRB.MAXIMIZE)

    m.update()

def set_edge_connectivity_objective(m, conservation, connectivity, pux, metric, pu_z, pu_m):
    pu = conservation.pu

    values_sum = pd.DataFrame(columns = ['pu1',  'pu2', 'value'])
    for condata in connectivity.get_connectivity_data():
        metric_values = condata.get_metric_values(metric).copy()
        #print(metric_values)
        values_sum = pd.concat([values_sum, metric_values], ignore_index=True)
    values_sum = normalize_edge(values_sum.groupby(['pu1', 'pu2']).value.sum().reset_index())
    #values_sum = values_sum.groupby(['pu1', 'pu2']).value.sum().reset_index()

    for pu1, pu2, val in zip(values_sum['pu1'], values_sum['pu2'], values_sum['value']):
        x_i = pux.loc[pux['pu'] == pu1, 'x'].item()
        x_j = pux.loc[pux['pu'] == pu2, 'x'].item()
        z = m.addVar(vtype=GRB.BINARY, name = "z_" + str(x_i) + "_" + str(x_j))
        m.addConstr(z == gp.and_([x_i, x_j]))
        pu_z.append(z)
        pu_m.append(val)

    return (pu_z, pu_m)


#TODO Multiple metrics set objective
def set_node_connectivity_objective(m, conservation, connectivity, pux, metric_k, pu_mx, pu_m):
    pu = conservation.pu

    #data_set = []
    for condata in connectivity.get_connectivity_data():
        # TODO add option to NOT normalize data?
        metric_values = condata.get_normalized_metric_values(metric_k).copy()

        #for pu_id in metric_values['pu']:
        #    print(pu_id)
        #    pu_m.append(metric_values.loc[metric_values['pu'] == pu_id, 'value'].item())
        #    pu_mx.append(pux.loc[pux['pu'] == pu_id, 'x'].item())
        for pu_id in pu['id']:
            if pu_id in metric_values['pu'].values:
                pu_m.append(metric_values.loc[metric_values['pu'] == pu_id, 'value'].item())
                pu_mx.append(pux.loc[pux['pu'] == pu_id, 'x'].item())
    # set objective: maximize sum(ci * xi for all pu i) + sum(x_i * metric_value_i)
    return (pu_mx, pu_m)

#def set_connectivity_objective(m, conservation, connectivity, pux):
#    pu = conservation.pu
#    pu_m = []
#    pu_mx = []
#
#    #data_set = []
#    for condata in connectivity.get_connectivity_data():
#        metric_values = []
#        for metric_k in condata.metrics:
#            # TODO add option to NOT normalize data?
#            metric_values = condata.get_normalized_metric_values(metric_k).copy()
#
#            #for pu_id in metric_values['pu']:
#            #    print(pu_id)
#            #    pu_m.append(metric_values.loc[metric_values['pu'] == pu_id, 'value'].item())
#            #    pu_mx.append(pux.loc[pux['pu'] == pu_id, 'x'].item())
#            for pu_id in pu['id']:
#                if pu_id in metric_values['pu'].values:
#                    pu_m.append(metric_values.loc[metric_values['pu'] == pu_id, 'value'].item())
#                    pu_mx.append(pux.loc[pux['pu'] == pu_id, 'x'].item())
#    # set objective: maximize sum(ci * xi for all pu i) + sum(x_i * metric_value_i)
#    m.setObjective(sum(pu_mx[j] * pu_m[j] for j in range(len(pu_m))), GRB.MAXIMIZE)
#    m.update()

def set_connectivity_blm_objective(m, conservation, connectivity, pux, blm):
    # blm penalty: select all xi vij and set and select all zij
    xi = []
    vij = []
    zij = []

    pu = conservation.pu
    pu_m = []
    pu_mx = []

    #data_set = []
    for condata in connectivity.get_connectivity_data():
        metric_values = []
        for metric_k in condata.metrics:
            # TODO add option to NOT normalize data?
            metric_values = condata.get_normalized_metric_values(metric_k).copy()

            for pu_id in pu['id']:
                if pu_id in metric_values['pu'].values:
                    pu_m.append(metric_values.loc[metric_values['pu'] == pu_id, 'value'].item())
                    pu_mx.append(pux.loc[pux['pu'] == pu_id, 'x'].item())
    # set objective: maximize sum(ci * xi for all pu i) + sum(x_i * metric_value_i)

    for i, j, v in zip(conservation.bounds['id1'], conservation.bounds['id2'], conservation.bounds['boundary']):
        x_i = pux.loc[pux['pu'] == i, 'x'].item()
        x_j = pux.loc[pux['pu'] == j, 'x'].item()
        xi.append(x_i)
        vij.append(v)

        # z makes sure penalty is only applied when x_i is selected, but x_j is not
        z = m.addVar(vtype=GRB.BINARY, name = "z_" + str(i) + "_" + str(j))
        m.addConstr(z == gp.and_([x_i, x_j]))
        zij.append(z)

    m.setObjective(sum(pu_mx[j] * pu_m[j] for j in range(len(pu_m))) - blm * sum(xi[j] * vij[j] - zij[j] * vij[j] for j in range(len(xi))), GRB.MAXIMIZE)

    m.update()

def set_cost_objective(m, conservation, pux):
    ''' set the objective function only minimizing the cost: min sum (ci xi) '''
    (pu_c, pu_x) = get_cost_and_selected_pu(m, conservation, pux)
    # set objective: minimize sum(ci * xi for all pu i)
    m.setObjective(sum(pu_x[i] * pu_c[i] for i in range(len(pu_c))), GRB.MINIMIZE)

def set_cost_blm_objective(m, conservation, pux, blm):
    ''' set the objective function only minimizing cost and blm '''
    xi = []
    vij = []
    zij = []

    (pu_c, pu_x) = get_cost_and_selected_pu(m, conservation, pux)

    # blm penalty: select all xi vij and set and select all zij
    for i, j, v in zip(conservation.bounds['id1'], conservation.bounds['id2'], conservation.bounds['boundary']):
        x_i = pux.loc[pux['pu'] == i, 'x'].item()
        x_j = pux.loc[pux['pu'] == j, 'x'].item()
        xi.append(x_i)
        vij.append(v)

        # z makes sure penalty is only applied when x_i is selected, but x_j is not
        z = m.addVar(vtype=GRB.BINARY, name = "z_" + str(i) + "_" + str(j))
        m.addConstr(z == gp.and_([x_i, x_j]))
        zij.append(z)

    # set objective: minimize sum(ci * xi for all pu i) + blm sum(sum(xv - zv))
    m.setObjective(sum(pu_x[i] * pu_c[i] for i in range(len(pu_c))) + blm * sum(xi[j] * vij[j] - zij[j] * vij[j] for j in range(len(xi))), GRB.MINIMIZE)


def set_objective(m, conservation, pux, blm, connectivity=None):
    ''' Set the objective function '''
    if connectivity and connectivity.strategy == 'cost-con':
        set_cost_metric_objective(m, conservation, connectivity, pux)
    elif connectivity and connectivity.strategy == 'con':
        set_connectivity_objective(m, conservation, connectivity, pux)
    elif connectivity and connectivity.strategy == 'con-blm':
        set_connectivity_blm_objective(m, conservation, connectivity, pux, blm)
    elif not blm:
        print("setting cost objective")
        set_cost_objective(m, conservation, pux)
    else:
        set_cost_blm_objective(m, conservation, pux, blm)

    m.update()

###                                        ###
# Model initialization                       #
###                                        ###

def solve_model(m, timer):
    ''' set timers and solve model '''
    timer.start_solver()
    m.optimize()
    # LP
    #m.relax()
    timer.stop()

def setup_model(m, conservation, pux, blm, connectivity=None):
    ''' set model constraints and objective function '''
    # set species consrtaints for all strategies
    print("setting species targets...")
    c_set_species_target(m, conservation, pux)

    if connectivity:
        if connectivity.strategy == 'cf':
            c_set_metric_target(m, conservation, connectivity, pux)
        elif connectivity.strategy == 'con' or connectivity.strategy == 'con-blm':
            c_set_cost_target(m, conservation, pux)

    # set objective
    print("setting objective...")
    set_objective(m, conservation, pux, blm, connectivity)

def init_pu_x(m, pu):
    ''' initialize dataframe containing decision variables x for each pu '''
    x = [None] * len(pu)
    for i in range(len(x)):
        x[i] = m.addVar(vtype=GRB.BINARY, name = "x_" + str(pu[i]))
        # LP
        #x[i] = m.addVar(vtype=GRB.CONTINUOUS, name = "x_" + str(pu[i]))
        m.addConstr(x[i] <= 1)
        m.addConstr(x[i] >= 0)

    m.update()
    return pd.DataFrame(list(zip(pu, x)), columns = ['pu', 'x'])

def set_gurobi_params(m, args):
    ''' set gurobi params according to provided arguments '''
    if args.gurobi_log:
        m.setParam('LogFile', args.gurobi_log)

    if args.time_limit:
        m.setParam('TimeLimit', args.time_limit)

    if args.gurobi_threads:
        m.setParam('Threads', args.gurobi_threads)

    if args.gap:
        m.setParam('MIPGap', args.gap)


def init_and_solve_model(args, conservation, timer, connectivity=None):
    ''' create model, setup constraints, solve and analyze the model '''
    # create Gurobi environment
    with gp.Env(empty=True) as env:
        if args.gurobi_mem:
            env.setParam("MemLimit", args.gurobi_mem)
        env.start()

        # create Gurobi model
        with gp.Model("Coco", env=env) as m:
            set_gurobi_params(m, args)

            # init pu decision vars
            print("initializing pux...")
            pux = init_pu_x(m, conservation.pu["id"])
            print("setting up model...")
            setup_model(m, conservation, pux, args.blm, connectivity)
            print("solving model...")
            solve_model(m, timer)

            # HPC
            #print_stats(args, timer, m)
            return process_solution(m, conservation, timer, pux)

def main():
    # setup timers
    timer = ctimer.Timer()
    timer.start_setup()

    # parse args
    args = cparser.parse_args()
    path = cio.process_path(args.input)

    # read files
    (species, pu, puvspr) = cio.read_standard_files(path)
    print("files read...")
    (conservation, connectivity) = init_conservation_and_connectivity(args, path, species, pu, puvspr)
    print("conservation created...")

    # init and solve model
    solution = init_and_solve_model(args, conservation, timer, connectivity)
    analyze_and_save_solution(args, conservation, solution, connectivity)

    cio.print_solution_stats(solution, conservation, timer)

if __name__ == '__main__':
    main()
