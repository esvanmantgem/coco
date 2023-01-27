import gurobipy as gp
import pandas as pd
import cocoio as cio
import cocoparser as cparser
import timer as ctimer
import connectivity as conn
import conservation as cons
import solution as sol
import constant as c
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
    if m.SolCount < 1:
        error = "The model is infeasible, no solution found"
        sys.exit(error)
    pu = conservation.pu
    pu_val = []
    pu_id = []
    xloc = []
    yloc = []
    for p, x in zip(pux[c.PUX_PID], pux[c.PUX_X]):
        pu_id.append(p)
        pu_val.append(1) if x.getAttr('Xn') >= 1 else pu_val.append(0)
        xloc.append(pu.loc[pu[c.PU_ID] == p, c.PU_XLOC].item())
        yloc.append(pu.loc[pu[c.PU_ID] == p, c.PU_YLOC].item())
    #df = pd.DataFrame(list(zip(pu_id, pu_val, xloc, yloc)), columns = ['pu', 'x', 'xloc', 'yloc'])
    df = pd.DataFrame(list(zip(pu_id, pu_val, xloc, yloc)), columns = [c.PU_ID, c.PUX_X, c.PU_XLOC, c.PU_YLOC])
    obj_val = m.getObjective().getValue()
    return sol.SolutionArea(df, obj_val, m.MIPGap, timer)

def process_lp_relaxation(m, conservation, timer, pux):
    pu = conservation.pu
    pu_val = []
    pu_id = []
    xloc = []
    yloc = []
    for p, x in zip(pux[c.PUX_PID], pux[c.PUX_X]):
        pu_id.append(p)
        pu_val.append(x.X)
        xloc.append(pu.loc[pu[c.PU_ID] == p, c.PU_XLOC].item())
        yloc.append(pu.loc[pu[c.PU_ID] == p, c.PU_YLOC].item())
    df = pd.DataFrame(list(zip(pu_id, pu_val, xloc, yloc)), columns = [c.PU_ID, c.PUX_X, c.PU_XLOC, c.PU_YLOC])
    obj_val = m.getObjective().getValue()
    return sol.SolutionArea(df, obj_val, None, timer)

def get_args_stats(args):
    arg_names = []
    arg_values = []
    for arg in vars(args):
        arg_names.append(arg)
        arg_values.append(getattr(args, arg))
    return pd.DataFrame(list(zip(arg_names, arg_values)), columns = [c.ARGS_NAME, c.ARGS_VAL])

def analyze_and_save_solution(args, conservation, solution, connectivity=None):
    ''' plot and show a solution map and write solution to 'solution.csv' '''
    path = args.output

    # analyze solution
    spec_sum = solution.features_sum(conservation)
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
        cio.save_csv(metric_sum, path, c.METRICS)

    # save csv files
    cio.save_csv(spec_sum, path, c.TARGETS)
    cio.save_csv(solution.pux, path, c.SOLUTION)
    cio.save_csv(arg_run_stats, path, c.RUNSTATS)

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
    elif args.feature_edgelist:
        for data in con_data:
            connectivity.set_feature_connectivity_edgelist(data, args.metric, pu_data)
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
    if c.EC in args.metric and pu_data is None:
        error = "equivalent connectivity: planning unit attribute file missing (--pu-data <attribute_file>)"
        sys.exit(error)
    if args.cmd == c.RSP_CF:
        metric_weight = args.metric_prop if args.metric_target == None else args.metric_target
        metric_target = False if args.metric_target == None else True
    elif args.cmd == c.RSP_CC:
        metric_weight = args.metric_weight
        metric_target = False
    #elif args.cmd == c.RSP_CON or args.cmd == con.RSP_BLM:
    elif args.cmd == c.RSP_CON:
        metric_weight = None
        metric_target = False

    # create new connectivity object, add all data and metrics.
    connectivity = conn.Connectivity(args.cmd, metric_weight, args.complete_graph, metric_target)
    if args.cmd == c.RSP_CC and args.cost_weight:
        connectivity.cost_weight = args.cost_weight
    set_connectivity_data(args, con_data, connectivity, pu_data)
    #set_metrics(args, connectivity)
    return connectivity

def init_connectivity(args, path):
    ''' initialize connectivity data '''
    con_data = cio.read_connectivity_data(path, args)
    pu_data = cio.read_pu_data(path, args.pu_data) if args.pu_data else None
    #if args.cmd == c.RSP_CF or args.cmd == c.RSP_CC or args.cmd == c.RSP_CON or args.cmd == c.RSP_BLM:
    if args.cmd == c.RSP_CF or args.cmd == c.RSP_CC or args.cmd == c.RSP_CON:
        return init_pre_connectivity(args, con_data, pu_data)
    #elif args.strategy == 'opt-live':
    #    error = "Live optimization of metric not implemented yet"
    #    exit(error)
    else:
        error = "Unknown strategy"
        sys.exit(error)

def init_bounds(args, path):
    file = args.featre_edgelist[0] if args.cmd == c.RSP_SD else c.BOUND_F
    bounds = pd.read_csv(cio.open_file(path, file))

    if args.cmd == c.RSP_SD:
        bounds = bounds.loc[bounds[c.BD_VAL] != 0].reset_index(drop=True)
        conservation.bounds = bounds.rename(columns={c.BD_VAL: c.BD_BOUND})
    return bounds

def init_conservation(args, pu, features, pvf, bounds):
    conservation = cons.Conservation(pu, features, pvf, args.cmd, bounds)
    #if args.cmd == c.RSP_CON or args.cmd == 'con-blm':
    if args.cmd == c.RSP_CON:
        conservation.max_cost = args.max_cost
        conservation.min_cost = args.min_cost if args.min_cost else None
    if args.cmd == c.RSP_BLM:
        conservation.blm_weight = args.blm_weight
    return conservation

def init_conservation_and_connectivity(args, path, features, pu, pvf):
    bounds = init_bounds(args, path) if args.cmd == c.RSP_BLM else None
    conservation = init_conservation(args, pu, features, pvf, bounds)
    connectivity = init_connectivity(args, path) if args.cmd != c.RSP else None
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

    # drop 0 values
    pu_values = pu_values.loc[(pu_values > 0)]
    if len(pu_values) == 0:
        return

    # select x of pu i and the amount of metric k in pu i
    for pu, value in zip(pu_ids, pu_values):
        x_pu = pux[pux[c.PUX_PID] == pu]
        xi.append(x_pu[c.PUX_X].item())
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
        x_pu = pux[pux[c.PUX_PID] == pu]
        xi.append(x_pu[c.PUX_X].item())
        rik.append(value)
    # add contraint to enforce the total amount of metric k in selected pu i's >= the target (or prop) of metric k
    m.addConstr(sum(xi[i] * rik[i] for i in range(len(xi))) <= tk)
    m.update()

def c_set_metric_target(m, conservation, connectivity, pux):
    for metric in connectivity.metrics:
        #if metric == 'betcent' or metric == c.INDEG or metric == c.OUTDEG:
        if metric == c.BC or metric == c.INDEG or metric == c.OUTDEG:
            c_set_node_metric_target(m, conservation, connectivity, pux, metric)
        elif metric == c.EC:
            c_set_edge_metric_target(m, conservation, connectivity, pux, metric)
    m.update()

def c_set_node_metric_target(m, conservation, connectivity, pux, metric_k):
    '''
    set target constraints for each metric
    sum(rik * xi) >= tk for all pu i, for all metrics k
    '''
    for condata in connectivity.get_connectivity_data():
        metric_values = condata.get_metric_values(metric_k)
        total = metric_values[c.MET_VAL].sum()

        # calculate tk based on proportion or target
        tk = connectivity.weight * total if not connectivity.target else connectivity.weight
        condata.get_metric(metric_k).set_target(tk)
        set_target_ge_constraint(m, pux, metric_values[c.MET_PID], metric_values[c.MET_VAL], tk)
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
        total = metric_values[c.MET_VAL].sum()

        for pu1, pu2, val in zip(metric_values[c.MET_PID1], metric_values[c.MET_PID2], metric_values[c.MET_VAL]):
            x_i = pux.loc[pux[c.PUX_PID] == pu1, c.PUX_X].item()
            x_j = pux.loc[pux[c.PUX_PID] == pu2, c.PUX_X].item()
            z = m.addVar(vtype=GRB.BINARY, name = "z_" + str(x_i) + "_" + str(x_j))
            m.addConstr(z == gp.and_([x_i, x_j]))
            pu_z.append(z)
            pu_m.append(val)

        # calculate tk based on proportion or target
        tk = connectivity.weight * total if not connectivity.target else connectivity.weight
        condata.get_metric(metric_k).set_target(tk)
        m.addConstr(sum(pu_z[i] * pu_m[i] for i in range(len(pu_z))) >= tk)

    m.update()

def c_set_cost_target(m, conservation, pux):
    # setting a max cost is mandatory for this strategy
    set_target_le_constraint(m, pux, conservation.pu[c.PU_ID], conservation.pu[c.PU_COST], conservation.max_cost)
    if conservation.min_cost:
        set_target_ge_constraint(m, pux, conservation.pu[c.PU_ID], conservation.pu[c.PU_COST], conservation.min_cost)

def c_set_features_target(m, conservation, pux):
    ''' set target constraints for each features
        sum(rik * xi) >= tk for all pu i, for all features k
    '''
    # group pvf in slices based on features_id giving all pu's for each features
    pu_per_sp = [y for x, y in conservation.pvf.groupby(c.PVF_FID)]
    for sp in pu_per_sp:
        # select features id from last row (index not possible)
        k = sp[c.PVF_FID].iloc[-1]
        tk = conservation.get_target(k)
        set_target_ge_constraint(m, pux, sp[c.PVF_PID], sp[c.PVF_VAL], tk)
        m.update()

###                                        ###
# Objective related functions                #
###                                        ###

def get_cost_and_selected_pu(m, conservation, pux):
    pu_c = []
    pu_x = []
    # cost objective: select all ci and xi
    for pu_id, pu_cost in zip(conservation.pu[c.PU_ID], conservation.pu[c.PU_COST]):
        pu_c.append(pu_cost)
        pu_x.append(pux.loc[pux[c.PUX_PID] == pu_id, c.PUX_X].item())
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
    #print("node: min = ", metric_values['value'].min(), " max = ", metric_values['value'].max())
    if metric_values[c.MET_VAL].min() != metric_values[c.MET_VAL].max():
        norm_data = (metric_values[c.MET_VAL] - metric_values[c.MET_VAL].min())/(metric_values[c.MET_VAL].max() - metric_values[c.MET_VAL].min())
        return pd.DataFrame(list(zip(metric_values[c.MET_PID], norm_data)), columns = [c.MET_PID, c.MET_VAL])
    else:
        # TODO: all values are the same, assume they are normalized (otherwise div by 0 error)
        print("No normalization needed, min is equal to max value")
        return metric_values

def normalize_edge(metric_values):
    #print("edge: min = ", metric_values['value'].min(), " max = ", metric_values['value'].max())
    if metric_values[c.MET_VAL].min() != metric_values[c.MET_VAL].max():
        norm_data = (metric_values[c.MET_VAL] - metric_values[c.MET_VAL].min())/(metric_values[c.MET_VAL].max() - metric_values[c.MET_VAL].min())
        return pd.DataFrame(list(zip(metric_values[c.MET_PID1], metric_values[c.MET_PID2], norm_data)), columns = [c.MET_PID1,  c.MET_PID2, c.MET_VAL])
    else:
        # TODO: all values are the same, assume they are normalized (otherwise div by 0 error)
        print("No normalization needed, edge min is equal to max")
        return metrics_values

def set_node_cost_metric_objective(m, conservation, connectivity, pux, metric, pu_mx, pu_m):
    pu = conservation.pu
    vs_pu = c.MET_PID
    vs_val = c.MET_VAL

    values_sum = pd.DataFrame(columns = [vs_pu, vs_val])
    for condata in connectivity.get_connectivity_data():
        print("setting metric node objective: ", metric)
        metric_values = condata.get_metric_values(metric).copy()
        values_sum = pd.concat([values_sum, metric_values], ignore_index=True)
    values_sum = normalize_node(values_sum.groupby([vs_pu]).value.sum().reset_index())

    for pu_id, pu_cost in zip(pu[c.PU_ID], pu[c.PU_COST]):
        if pu_id in values_sum[vs_pu].values:
            pu_m.append(values_sum.loc[values_sum[vs_pu] == pu_id, vs_val].item())
            pu_mx.append(pux.loc[pux[c.PUX_PID] == pu_id, c.PUX_X].item())

    return (pu_mx, pu_m)

def set_edge_cost_metric_objective(m, conservation, connectivity, pux, metric, pu_z, pu_m):
    pu = conservation.pu
    vs_pu1 = c.MET_PID1
    vs_pu2 = c.MET_PID2
    vs_val = c.MET_VAL

    values_sum = pd.DataFrame(columns = [vs_pu1, vs_pu2, vs_val])
    for condata in connectivity.get_connectivity_data():
        print("setting metric edge objective: ", metric)
        metric_values = condata.get_metric_values(metric).copy()
        #print(metric_values)
        values_sum = pd.concat([values_sum, metric_values], ignore_index=True)
    values_sum = normalize_edge(values_sum.groupby([vs_pu1, vs_pu2]).value.sum().reset_index())
    #values_sum = values_sum.groupby(['pu1', 'pu2']).value.sum().reset_index()

    for pu1, pu2, val in zip(values_sum[vs_pu1], values_sum[vs_pu2], values_sum[vs_val]):
        x_i = pux.loc[pux[c.PUX_PID] == pu1, c.PUX_X].item()
        x_j = pux.loc[pux[c.PUX_PID] == pu2, c.PUX_X].item()
        z = m.addVar(vtype=GRB.BINARY, name = "z_" + str(x_i) + "_" + str(x_j))
        m.addConstr(z == gp.and_([x_i, x_j]))
        pu_z.append(z)
        pu_m.append(val)

    return (pu_z, pu_m)

def set_cost_metric_objective(m, conservation, connectivity, pux):
    (pu_c, pu_x) = get_cost_and_selected_pu(m, conservation, pux)
    dec_vars = []
    dec_values = []

    for metric in connectivity.metrics:
        #if metric == 'betcent' or metric == c.INDEG or metric == c.OUTDEG:
        if metric == c.BC or metric == c.INDEG or metric == c.OUTDEG:
#            print("------------------------------------------- metric", metric)
            (dec_vars, dec_values) = set_node_cost_metric_objective(m, conservation, connectivity, pux, metric, dec_vars, dec_values)
        elif metric == c.EC:
#            print("------------------------------------------- metric", metric)
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
#        print("------------------------------------------- metric", metric)
        if metric == c.BC or metric == c.INDEG or metric == c.OUTDEG:
            (dec_vars, dec_values) = set_node_connectivity_objective(m, conservation, connectivity, pux, metric, dec_vars, dec_values)
        elif metric == c.EC:
            (dec_vars, dec_values) = set_edge_connectivity_objective(m, conservation, connectivity, pux, metric, dec_vars, dec_values)

    m.setObjective(sum(dec_vars[j] * dec_values[j] for j in range(len(dec_vars))), GRB.MAXIMIZE)

    m.update()

def set_edge_connectivity_objective(m, conservation, connectivity, pux, metric, pu_z, pu_m):
    pu = conservation.pu
    vs_pu1 = c.MET_PID1
    vs_pu2 = c.MET_PID2
    vs_val = c.MET_VAL

    values_sum = pd.DataFrame(columns = [vs_pu1,  vs_pu2, vs_val])
    for condata in connectivity.get_connectivity_data():
        metric_values = condata.get_metric_values(metric).copy()
        #print(metric_values)
        values_sum = pd.concat([values_sum, metric_values], ignore_index=True)
    values_sum = normalize_edge(values_sum.groupby([vs_pu1, vs_pu2]).value.sum().reset_index())
    #values_sum = values_sum.groupby(['pu1', 'pu2']).value.sum().reset_index()

    for pu1, pu2, val in zip(values_sum[vs_pu1], values_sum[vs_pu2], values_sum[vs_val]):
        x_i = pux.loc[pux[c.PUX_PID] == pu1, c.PUX_X].item()
        x_j = pux.loc[pux[c.PUX_PID] == pu2, c.PUX_X].item()
        z = m.addVar(vtype=GRB.BINARY, name = "z_" + str(x_i) + "_" + str(x_j))
        m.addConstr(z == gp.and_([x_i, x_j]))
        pu_z.append(z)
        pu_m.append(val)

    return (pu_z, pu_m)

def set_node_connectivity_objective(m, conservation, connectivity, pux, metric_k, pu_mx, pu_m):
    pu = conservation.pu

    for condata in connectivity.get_connectivity_data():
        # TODO add option to NOT normalize data?
        metric_values = condata.get_normalized_metric_values(metric_k).copy()

        for pu_id in pu[c.PU_ID]:
            if pu_id in metric_values[c.MET_PID].values:
                pu_m.append(metric_values.loc[metric_values[c.MET_PID] == pu_id, c.MET_VAL].item())
                pu_mx.append(pux.loc[pux['pu'] == pu_id, 'x'].item())
    return (pu_mx, pu_m)

def set_cost_objective(m, conservation, pux):
    ''' set the objective function only minimizing the cost: min sum (ci xi) '''
    (pu_c, pu_x) = get_cost_and_selected_pu(m, conservation, pux)
    # set objective: minimize sum(ci * xi for all pu i)
    m.setObjective(sum(pu_x[i] * pu_c[i] for i in range(len(pu_c))), GRB.MINIMIZE)

def set_cost_blm_objective(m, conservation, pux):
    ''' set the objective function only minimizing cost and blm '''
    xi = []
    vij = []
    zij = []

    (pu_c, pu_x) = get_cost_and_selected_pu(m, conservation, pux)

    # blm penalty: select all xi vij and set and select all zij
    for i, j, v in zip(conservation.bounds[c.BD_PID1], conservation.bounds[c.BD_PID2], conservation.bounds[c.BD_BOUND]):
        x_i = pux.loc[pux[c.PUX_PID] == i, c.PUX_X].item()
        x_j = pux.loc[pux[c.PUX_PID] == j, c.PUX_X].item()
        xi.append(x_i)
        vij.append(v)

        # z makes sure penalty is only applied when x_i is selected, but x_j is not
        z = m.addVar(vtype=GRB.BINARY, name = "z_" + str(i) + "_" + str(j))
        m.addConstr(z == gp.and_([x_i, x_j]))
        zij.append(z)

    # set objective: minimize sum(ci * xi for all pu i) + blm sum(sum(xv - zv))
    m.setObjective(sum(pu_x[i] * pu_c[i] for i in range(len(pu_c))) + conservation.blm_weight * sum(xi[j] * vij[j] - zij[j] * vij[j] for j in range(len(xi))), GRB.MINIMIZE)


def set_objective(m, conservation, pux, connectivity=None):
    ''' Set the objective function '''
    if connectivity and connectivity.strategy == c.RSP_CC:
        set_cost_metric_objective(m, conservation, connectivity, pux)
    elif connectivity and connectivity.strategy == c.RSP_CON:
        set_connectivity_objective(m, conservation, connectivity, pux)
    #elif connectivity and connectivity.strategy == 'con-blm':
    #    set_connectivity_blm_objective(m, conservation, connectivity, pux, blm)
    elif conservation.strategy == c.RSP_BLM:
        set_cost_blm_objective(m, conservation, pux)
    elif conservation.strategy == c.RSP_CF or conservation.strategy == c.RSP:
        set_cost_objective(m, conservation, pux)
    else:
        error = "Unknown strategy, objective can not be set"
        sys.exit(error)

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

def setup_model(m, conservation, pux, connectivity=None):
    ''' set model constraints and objective function '''
    # set features consrtaints for all strategies
    print("setting features targets...")
    c_set_features_target(m, conservation, pux)

    if connectivity:
        if connectivity.strategy == c.RSP_CF:
            c_set_metric_target(m, conservation, connectivity, pux)
        #elif connectivity.strategy == c.RSP_CON or connectivity.strategy == 'con-blm':
        elif connectivity.strategy == c.RSP_CON:
            c_set_cost_target(m, conservation, pux)

    # set objective
    print("setting objective...")
    set_objective(m, conservation, pux, connectivity)

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
    return pd.DataFrame(list(zip(pu, x)), columns = [c.PUX_PID, c.PUX_X])

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
            pux = init_pu_x(m, conservation.pu[c.PU_ID])
            print("setting up model...")
            setup_model(m, conservation, pux, connectivity)
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
    (features, pu, pvf) = cio.read_standard_files(path)
    print("files read...")
    (conservation, connectivity) = init_conservation_and_connectivity(args, path, features, pu, pvf)
    print("conservation created...")

    # init and solve model
    solution = init_and_solve_model(args, conservation, timer, connectivity)
    analyze_and_save_solution(args, conservation, solution, connectivity)

    cio.print_solution_stats(solution, conservation, timer)

if __name__ == '__main__':
    main()
