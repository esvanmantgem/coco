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

import gurobipy as gp
import pandas as pd
import numpy as np
import cocoio as cio
import cocoparser as cparser
import timer as ctimer
import rsp.connectivity as conn
import rsp.conservation as cons
import rsp.solution as sol
import constant as c
import sys
from gurobipy import GRB

###                                        ###
# Analysis and output functions              #
###                                        ###

def process_solution(m, conservation, timer):
    """
    Processes the ILP solution and timers, creates and returns the results

    Parameters
    ----------
    m : Gurobi model
        Model in Gurobi environment
    conservation : Conservation
        Conservation object (pu, features, pvf, strategy, bounds)
    timer : Timer
        Timer object containing start, end times and functions
    Returns
    -------
    A solution area object containing all info on the solution
    """
    # LP
    #lp = True
    #if lp:
    #    return process_lp_relaxation(m, conservation, timer, pux)
    #else:
    if m.SolCount < 1:
        error = "The model is infeasible, no solution found"
        sys.exit(error)
    pu = conservation.pu
    pu_val = []
    pu_id = conservation.pu['pu']
    xloc = conservation.pu['xloc']
    yloc = conservation.pu['yloc']
    for x in conservation.pu[c.PUX_X]:
        pu_val.append(1) if x.getAttr('Xn') >= 1 else pu_val.append(0)
    #df = pd.DataFrame(list(zip(pu_id, pu_val, xloc, yloc)), columns = ['pu', 'x', 'xloc', 'yloc'])
    df = pd.DataFrame(list(zip(pu_id, pu_val, xloc, yloc)), columns = [c.PU_ID, c.PUX_X, c.PU_XLOC, c.PU_YLOC])
    obj_val = m.getObjective().getValue()
    return sol.SolutionArea(df, obj_val, m.MIPGap, timer)

#def process_lp_relaxation(m, conservation, timer):
#    """
#    LP Relaxation stuff, TODO for prioritization, not used now
#    Parameters
#    ----------
#    m : Gurobi model
#        Model in Gurobi environment
#    conservation : Conservation
#        Conservation object (pu, features, pvf, strategy, bounds)
#    timer : Timer
#        Timer object containing start, end times and functions
#    pux : Pandas DataFrame
#        DataFrame containing all pu id's and decision variables x [pu_id, pu_x]
#    Returns
#    -------
#    SolutionArea area
#    """
#    pu = conservation.pu
#    pu_val = []
#    pu_id = []
#    xloc = []
#    yloc = []
#    for p, x in zip(pux[c.PUX_PID], pux[c.PUX_X]):
#        pu_id.append(p)
#        pu_val.append(x.X)
#        xloc.append(pu.loc[pu[c.PU_ID] == p, c.PU_XLOC].item())
#        yloc.append(pu.loc[pu[c.PU_ID] == p, c.PU_YLOC].item())
#    df = pd.DataFrame(list(zip(pu_id, pu_val, xloc, yloc)), columns = [c.PU_ID, c.PUX_X, c.PU_XLOC, c.PU_YLOC])
#    obj_val = m.getObjective().getValue()
#    return sol.SolutionArea(df, obj_val, None, timer)

def get_args_stats(args):
    """
    Creates a new Pandas DataFrame containting all the arguments and corresponding values

    Parameters
    ----------
    args : Argparse namespace
        Contains all passed arguments.

    Returns
    -------
    Pandas DataFrame containting all the arguments and corresponding values
    """

    arg_names = []
    arg_values = []
    for arg in vars(args):
        arg_names.append(arg)
        arg_values.append(getattr(args, arg))
    return pd.DataFrame(list(zip(arg_names, arg_values)), columns = [c.ARGS_NAME, c.ARGS_VAL])

def analyze_and_save_solution(args, conservation, solution, connectivity=None):
    """
    Plot and show a solution map and write solution to 'solution.csv'

    Parameters
    ----------
    args : Argparse namespace
        Contains all passed arguments.
    conservation : Conservation
        Conservation object (pu, features, pvf, strategy, bounds)
    connectivity : Connectivity
        Connectivity object (strategy, weight, complete_graph, target), can be None if RSP without connectivity

    Returns
    -------
    None
    """

    path = args.output

    # analyze solution
    spec_sum = solution.features_sum(conservation)
    run_stats = solution.save_run_stats(conservation)
    arg_stats = get_args_stats(args)
    arg_run_stats = pd.concat([run_stats, arg_stats])

    if connectivity:
        metric_sum = solution.metrics_sum(connectivity)
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
    """
    Drops values of the calculated connectivity metric below or above specified thresholds

    Parameters
    ----------
    args : Argparse namespace
        Contains all passed arguments.
    connectivity : Connectivity
        Connectivity object (strategy, weight, complete_graph, target)

    Returns
    -------
    None
    """

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

def set_connectivity_data(args, con_data, connectivity, conservation, pu_data=None):
    """
    Adds the connectivity data sets and calculates all metric values on each dataset

    Parameters
    ----------
    args : Argparse namespace
        Contains all passed arguments.
    con_data : list
        A list of Pandas DataFrames containing all connectivity data provided as matrix or edgelist
    connectivity : Connectivity
        Connectivity object (strategy, weight, complete_graph, target)
    pu_data : Pandas DataFrame
        DataFrame containing all info on planning unit attribute data if provided (feature id, pu id, value)

    Returns
    -------
    The connectivity object with all connectivity datasets added
    """

    if args.con_matrix:
        for i in range(len(con_data)):
            connectivity.set_connectivity_matrix(con_data[i], i, args.metric, pu_data)
    elif args.con_edgelist:
        for i in range(len(con_data)):
            connectivity.set_connectivity_edgelist(con_data[i], i, args.metric, pu_data)
    elif args.feature_edgelist:
        for data in con_data:
            connectivity.set_feature_connectivity_edgelist(data, args.metric, pu_data, conservation)
    else:
        error = "Please give connectivity input file"
        sys.exit(error)
    #if args.pu_data:
        #for data in pu_data:
    #    connectivity.set_pu_data(pu_data)
    process_metric_threshold_values(args, connectivity)

def init_pre_connectivity(args, con_data, conservation, pu_data=None):
    """
    Creates a new connectivity object and initializes it

    Parameters
    ----------
    args : Argparse namespace
        Contains all passed arguments.
    con_data : list
        A list of Pandas DataFrames containing all connectivity data provided as matrix or edgelist
    pu_data : Pandas DataFrame
        DataFrame containing all info on planning unit attribute data if provided (feature id, pu id, value)

    Returns
    -------
    A new initialized connectivity object

    """

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
    elif args.cmd == c.RSP_CON:
        metric_weight = None
        metric_target = False

    # create new connectivity object, add all data and metrics.
    connectivity = conn.Connectivity(args.cmd, metric_weight, args.complete_graph, metric_target)
    if args.cmd == c.RSP_CC and args.cost_weight:
        connectivity.cost_weight = args.cost_weight
    set_connectivity_data(args, con_data, connectivity, conservation, pu_data)
    return connectivity

def init_connectivity(args, path, conservation):
    """
    Creates and initializes a new connectivity object

    Parameters
    ----------
    args : Argparse namespace
        Contains all passed arguments.
    path : str
        Path to input folder
    Returns
    -------
    A new connectivity object
    """

    con_data = cio.read_connectivity_data(path, args)
    pu_data = cio.read_pu_data(path, args.pu_data) if args.pu_data else None
    #if args.cmd == c.RSP_CF or args.cmd == c.RSP_CC or args.cmd == c.RSP_CON or args.cmd == c.RSP_BLM:
    if args.cmd == c.RSP_CF or args.cmd == c.RSP_CC or args.cmd == c.RSP_CON:
        return init_pre_connectivity(args, con_data, conservation, pu_data)
    #elif args.strategy == 'opt-live':
    #    error = "Live optimization of metric not implemented yet"
    #    exit(error)
    else:
        error = "Unknown strategy"
        sys.exit(error)

def init_bounds(args, path):
    """
    Initializes the bounds file

    Parameters
    ----------
    args : Argparse namespace
        Contains all passed arguments.
    path : str
        Path to input folder
    Returns
    -------
    Bounds
    """

    file = args.featre_edgelist[0] if args.cmd == c.RSP_SD else c.BOUND_F
    bounds = pd.read_csv(cio.open_file(path, file))

    if args.cmd == c.RSP_SD:
        bounds = bounds.loc[bounds[c.BD_VAL] != 0].reset_index(drop=True)
        conservation.bounds = bounds.rename(columns={c.BD_VAL: c.BD_BOUND})
    return bounds

def init_conservation(args, pu, features, pvf, bounds):
    """
    Creates and initializes a new conservation object

    Parameters
    ----------
    args : Argparse namespace
        Contains all passed arguments.
    pu : Pandas DataFrame
        DataFrame containing info from pu.csv (pu, cost, xloc, yloc)
    features : Pandas DataFrame
        DataFrame containing info from features.csv (id, prop/target)
    pvf : Pandas DataFrame
        DataFrame containing info from pvf.csv (feature id, pu id, value)
    Returns
    -------
    A new instance of Conservation
    """

    conservation = cons.Conservation(pu, features, pvf, args.cmd, bounds)
    if args.cmd == c.RSP_CON:
        conservation.max_cost = args.max_cost
        conservation.min_cost = args.min_cost if args.min_cost else None
    if args.cmd == c.RSP_BLM:
        conservation.blm_weight = args.blm_weight
    return conservation

def init_conservation_and_connectivity(args, path, features, pu, pvf):
    """
    Initialize the conservation object and if needed the connectivity object

    Initializes the conservation. If the RSP variant is not RSP-Cost, initializes connectivity
    Parameters
    ----------
    args : Argparse namespace
        Contains all passed arguments.
    path : str
        Path to input folder
    features : Pandas DataFrame
        DataFrame containing info from features.csv (id, prop/target)
    pu : Pandas DataFrame
        DataFrame containing info from pu.csv (pu, cost, xloc, yloc)
    pvf : Pandas DataFrame
        DataFrame containing info from pvf.csv (feature id, pu id, value)
    Returns
    -------
    A tuple (conservation, connectivity), where connectivity is None if RSP-Cost
    """

    bounds = init_bounds(args, path) if args.cmd == c.RSP_BLM else None
    conservation = init_conservation(args, pu, features, pvf, bounds)
    connectivity = init_connectivity(args, path, conservation) if args.cmd != c.RSP else None
    return (conservation, connectivity)

###                                        ###
# Constraints related functions              #
###                                        ###

def c_set_node_metric_target(m, conservation, connectivity, metric):
    """
    Set target constraints for each node weighted metric in RSP-CF

    Add constraints sum(rik * xi) >= tk for all pu i, for all node weighted metrics k

    Parameters
    ----------
    m : Gurobi model
        Model in Gurobi environment
    conservation : Conservation
        Conservation object (pu, features, pvf, strategy, bounds)
    metric : str
        The name of the metric to add the constraint for
    Returns
    -------
    None
    """

    for condata in connectivity.get_connectivity_data():
        metric_values = condata.get_metric_values(metric)
        total = metric_values[c.MET_VAL].sum()

        # calculate tk based on proportion or target
        target = connectivity.weight * total if not connectivity.target else connectivity.weight
        condata.get_metric(metric).set_target(target)

        metric_values = metric_values.merge(conservation.pu[c.PUX_X], left_on=c.PU_ID, right_on=conservation.pu[c.PU_ID])

        x = metric_values[c.PUX_X].to_numpy()
        values = metric_values[c.MET_VAL].to_numpy()

        m.addConstr(sum(x[i] * values[i] for i in range(len(x))) >= target)
    m.update()

def c_set_edge_metric_target(m, conservation, connectivity, metric):
    """
    Set target constraints for each edge weighted metric in RSP-CF

    Add constraints sum(rik * xi * yi) >= tk for all pu i, for all edge weighted metrics k

    Parameters
    ----------
    m : Gurobi model
        Model in Gurobi environment
    conservation : Conservation
        Conservation object (pu, features, pvf, strategy, bounds)
    connectivity : Connectivity
        Connectivity object (strategy, weight, complete_graph, target)
    metric : str
        The name of the metric to add the constraint for
    Returns
    -------
    None
    """

    for condata in connectivity.get_connectivity_data():
        pu_z = []
        metric_values = condata.get_metric_values(metric)
        total = metric_values[c.MET_VAL].sum()

        target = connectivity.weight * total if not connectivity.target else connectivity.weight
        condata.get_metric(metric).set_target(target)

        metric_values = metric_values.merge(conservation.pu[c.PUX_X], left_on=c.MET_PID1, right_on=conservation.pu[c.PU_ID])
        metric_values = metric_values.merge(conservation.pu[c.PUX_X], left_on=c.MET_PID2, right_on=conservation.pu[c.PU_ID])

        x_1 = metric_values['x_x'].to_numpy()
        x_2 = metric_values['x_y'].to_numpy()

        for x_i, x_j in zip(x_1, x_2):
            z = m.addVar(vtype=GRB.BINARY, name = "z_" + str(x_i) + "_" + str(x_j))
            m.addConstr(z == gp.and_([x_i, x_j]))
            pu_z.append(z)

        metric_values[c.PUX_X] = pu_z

        # calculate tk based on proportion or target
        x = metric_values[c.PUX_X].to_numpy()
        pu_m = metric_values[c.MET_VAL].to_numpy()

        m.addConstr(sum(x[i] * pu_m[i] for i in range(len(x))) >= target)
    m.update()

def c_set_metric_target(m, conservation, connectivity):
    """
    Set the connectivity metric targets for RSP-CF

    Select the correct function to add the constraints depending on the metric (node or edge weighted)
    Parameters
    ----------
    m : Gurobi model
        Model in Gurobi environment
    conservation : Conservation
        Conservation object (pu, features, pvf, strategy, bounds)
    connectivity : Connectivity
        Connectivity object (strategy, weight, complete_graph, target)
    Returns
    -------
    None
    """

    for metric in connectivity.metrics:
        #if metric == 'betcent' or metric == c.INDEG or metric == c.OUTDEG:
        if metric == c.BC or metric == c.INDEG or metric == c.OUTDEG:
            c_set_node_metric_target(m, conservation, connectivity, metric)
        elif metric == c.EC:
            c_set_edge_metric_target(m, conservation, connectivity, metric)
    m.update()

def c_set_cost_target(m, conservation):
    """
    Set the target for the cost in RSP-Con

    Parameters
    ----------
    m : Gurobi model
        Model in Gurobi environment
    conservation : Conservation
        Conservation object (pu, features, pvf, strategy, bounds)
    Returns
    -------
    None
    """

    x = conservation.pu[c.PUX_X].to_numpy()
    values = conservation.pu[c.PU_COST].to_numpy()
    # setting a max cost is mandatory for this strategy
    m.addConstr(sum(x[i] * values[i] for i in range(len(x))) <= conservation.max_cost)
    if conservation.min_cost:
        m.addConstr(sum(x[i] * values[i] for i in range(len(x))) >= conservation.min_cost)

def c_set_features_target(m, conservation):
    """
    Set feature target constraints

    For each feature sum(rik * xi) >= tk for all pu i, for all features k

    Parameters
    ----------
    m : Gurobi model
        Model in Gurobi environment
    conservation : Conservation
        Conservation object (pu, features, pvf, strategy, bounds)
    Returns
    -------
    None
    """

    # group pvf in slices based on features_id giving all pu's for each features
    pu_per_feature = [y for x, y in conservation.pvf.groupby(c.PVF_FID)]
    for feature in pu_per_feature:
        # select features id from last row (index not possible)
        if (conservation.has_target(feature[c.PVF_FID].iloc[-1])):
            target = conservation.get_target(feature[c.PVF_FID].iloc[-1])
            feature = feature.merge(conservation.pu[c.PUX_X], left_on=c.PU_ID, right_on=conservation.pu[c.PU_ID])

            x = feature[c.PUX_X].to_numpy()
            values = feature[c.PVF_VAL].to_numpy()

            m.addConstr(sum(x[i] * values[i] for i in range(len(x))) >= target)
            m.update()

###                                        ###
# Objective related functions                #
###                                        ###

def get_cost_and_selected_pu(m, conservation):

    """
    Selects the cost and decision variable of all planning units

    Parameters
    ----------
    m : Gurobi model
        Model in Gurobi environment
    conservation : Conservation
        Conservation object (pu, features, pvf, strategy, bounds)
    Returns
    -------
    A tuple (pu_c, pu_x) of two lists, in which each index has the cost (pu_c) and decision variable (pu_x) of a planning unit

    """
    pu_c = conservation.pu['cost'].to_numpy()
    pu_x = conservation.pu['x'].to_numpy()

    return (pu_c, pu_x)

def set_edge_connectivity_objective(m, conservation, connectivity, metric, pu_z, pu_m):
    """
    Select the decision vars and the values for the edge weighted connectivity metric objective.

    Gets the metric values for all connectivity data sets and adds the decision var and the value to two seperate lists, s.t., each index in both lists is one pu_x - metric value pair.

    Parameters
    ----------
    m : Gurobi model
        Model in Gurobi environment
    conservation : Conservation
        Conservation object (pu, features, pvf, strategy, bounds)
    connectivity : Connectivity
        Connectivity object (strategy, weight, complete_graph, target)
    metric : str
        Name of the metric that needs to be set
    pu_mx : list
        Ordered list containing the decision vars of the pu's. New decision vars are added
    pu_m : list
        Ordered list containing the values of the pu's. New values are added

    Returns
    -------
    A tuple of two ordered lists (pu_mx, pu_m) containing the value and dec var of pu's to be added to the objective
    """

    pu = conservation.pu
    vs_pu1 = c.MET_PID1
    vs_pu2 = c.MET_PID2
    vs_val = c.MET_VAL

    for condata in connectivity.get_connectivity_data():
        metric_values = condata.get_normalized_metric_values(metric).copy()

        metric_values = metric_values.merge(conservation.pu[c.PUX_X], left_on=c.MET_PID1, right_on=conservation.pu[c.PU_ID])
        metric_values = metric_values.merge(conservation.pu[c.PUX_X], left_on=c.MET_PID2, right_on=conservation.pu[c.PU_ID])

        x_1 = metric_values['x_x'].to_numpy()
        x_2 = metric_values['x_y'].to_numpy()

        for x_i, x_j in zip(x_1, x_2):
            z = m.addVar(vtype=GRB.BINARY, name = "z_" + str(x_i) + "_" + str(x_j))
            m.addConstr(z == gp.and_([x_i, x_j]))
            pu_z.append(z)

        pu_m = np.append(pu_m, metric_values[c.MET_VAL].to_numpy())

    return (pu_z, pu_m)

def set_node_connectivity_objective(m, conservation, connectivity, metric, pu_mx, pu_m):
    """
    Select the decision vars and the values for the node weighted connectivity metric objective.

    Gets the metric values for all connectivity data sets and adds the decision var and the value to two seperate lists, s.t., each index in both lists is one pu_x - metric value pair. Normalize the values per connectivity data set separetely

    Parameters
    ----------
    m : Gurobi model
        Model in Gurobi environment
    conservation : Conservation
        Conservation object (pu, features, pvf, strategy, bounds)
    connectivity : Connectivity
        Connectivity object (strategy, weight, complete_graph, target)
    metric : str
        Name of the metric that needs to be set
    pu_mx : list
        Ordered list containing the decision vars of the pu's. New decision vars are added
    pu_m : list
        Ordered list containing the values of the pu's. New values are added

    Returns
    -------
    A tuple of two ordered lists (pu_mx, pu_m) containing the value and dec var of pu's to be added to the objective

    """

    for condata in connectivity.get_connectivity_data():
        # TODO add option to NOT normalize data?
        metric_values = condata.get_normalized_metric_values(metric).copy()
        metric_values = metric_values.merge(conservation.pu[c.PUX_X], left_on=c.PU_ID, right_on=conservation.pu[c.PU_ID])

        pu_mx = np.append(pu_mx, metric_values[c.PUX_X].to_numpy())
        pu_m = np.append(pu_m, metric_values[c.MET_VAL].to_numpy())
    return (pu_mx, pu_m)

def set_connectivity_objective(m, conservation, connectivity):
    """
    Set the objective with connectivity (RSP-Con)

    For each metric call the correct function to get the pu values and x's (vertex-weighted) or the edge values and z's (edge weighted) and add them to a list. Then, set the objective for all elements in the list. The lists are ordered and must be iterated over simultaneously.

    Parameters
    ----------
    m : Gurobi model
        Model in Gurobi environment
    conservation : Conservation
        Conservation object (pu, features, pvf, strategy, bounds)
    connectivity : Connectivity
        Connectivity object (strategy, weight, complete_graph, target)

    Returns
    -------
    None
    """

    (pu_c, pu_x) = get_cost_and_selected_pu(m, conservation)
    dec_vars = []
    dec_values = []

    for metric in connectivity.metrics:
#        print("------------------------------------------- metric", metric)
        if metric == c.BC or metric == c.INDEG or metric == c.OUTDEG:
            (dec_vars, dec_values) = set_node_connectivity_objective(m, conservation, connectivity, metric, dec_vars, dec_values)
        elif metric == c.EC:
            (dec_vars, dec_values) = set_edge_connectivity_objective(m, conservation, connectivity, metric, dec_vars, dec_values)

    #dec_vars = dec_vars.to_numpy()
    #dec_values = dec_values.to_numpy()

    m.setObjective(sum(dec_vars[j] * dec_values[j] for j in range(len(dec_vars))), GRB.MAXIMIZE)

    m.update()

def set_cost_connectivity_objective(m, conservation, connectivity):
    """
    Set the RSP-CC objective: min (ci xi) + max (mi xi).

    Select the correct node or edge weighted function to add the values to the tuple (xi, val_i) for all datasets for all metrics.

    Parameters
    ----------
    m : Gurobi model
        Model in Gurobi environment
    conservation : Conservation
        Conservation object (pu, features, pvf, strategy, bounds)
    connectivity : Connectivity
        Connectivity object (strategy, weight, complete_graph, target)

    Returns
    -------
    None
    """

    (pu_c, pu_x) = get_cost_and_selected_pu(m, conservation)
    dec_vars = []
    dec_values = []

    for metric in connectivity.metrics:
        if metric == c.BC or metric == c.INDEG or metric == c.OUTDEG:
            (dec_vars, dec_values) = set_node_connectivity_objective(m, conservation, connectivity, metric, dec_vars, dec_values)
        elif metric == c.EC:
            (dec_vars, dec_values) = set_edge_connectivity_objective(m, conservation, connectivity, metric, dec_vars, dec_values)

    #dec_vars = dec_vars.to_numpy()
    #dec_values = dec_values.to_numpy()

    m.setObjective((connectivity.cost_weight * sum(pu_x[i] * pu_c[i] for i in range(len(pu_c)))) -
                   connectivity.weight *
                   sum(dec_vars[j] * dec_values[j] for j in range(len(dec_vars))), GRB.MINIMIZE)
    m.update()

def set_cost_objective(m, conservation):
    """
    Set the RSP-CF objective: min sum(ci xi)

    Parameters
    ----------
    m : Gurobi model
        Model in Gurobi environment
    conservation : Conservation
        Conservation object (pu, features, pvf, strategy, bounds)
    Returns
    -------
    None
    """

    (pu_c, pu_x) = get_cost_and_selected_pu(m, conservation)

    # set objective: minimize sum(ci * xi for all pu i)
    m.setObjective(sum(pu_x[i] * pu_c[i] for i in range(len(pu_c))), GRB.MINIMIZE)

#def set_cost_blm_objective(m, conservation):
#    """
#    Set the objective for the RSP-BLM.
#
#    Parameters
#    ----------
#    m : Gurobi model
#        Model in Gurobi environment
#    conservation : Conservation
#        Conservation object (pu, features, pvf, strategy, bounds)
#    Returns
#    -------
#    None
#    """
#
#    xi = []
#    vij = []
#    zij = []
#
#    (pu_c, pu_x) = get_cost_and_selected_pu(m, conservation)
#
#    # blm penalty: select all xi vij and set and select all zij
#    for i, j, v in zip(conservation.bounds[c.BD_PID1], conservation.bounds[c.BD_PID2], conservation.bounds[c.BD_BOUND]):
#        x_i = pux.loc[pux[c.PUX_PID] == i, c.PUX_X].item()
#        x_j = pux.loc[pux[c.PUX_PID] == j, c.PUX_X].item()
#        xi.append(x_i)
#        vij.append(v)
#
#        # z makes sure penalty is only applied when x_i is selected, but x_j is not
#        z = m.addVar(vtype=GRB.BINARY, name = "z_" + str(i) + "_" + str(j))
#        m.addConstr(z == gp.and_([x_i, x_j]))
#        zij.append(z)
#
#    # set objective: minimize sum(ci * xi for all pu i) + blm sum(sum(xv - zv))
#    m.setObjective(sum(pu_x[i] * pu_c[i] for i in range(len(pu_c))) + conservation.blm_weight * sum(xi[j] * vij[j] - zij[j] * vij[j] for j in range(len(xi))), GRB.MINIMIZE)

def set_objective(m, conservation, connectivity=None):
    """
    Select the correct function to set the objective depending on the RSP variant

    Parameters
    ----------
    m : Gurobi model
        Model in Gurobi environment
    conservation : Conservation
        Conservation object (pu, features, pvf, strategy, bounds)
    connectivity : Connectivity
        Connectivity object (strategy, weight, complete_graph, target), can be None if RSP without connectivity
    Returns
    -------
    None
    """

    if connectivity and connectivity.strategy == c.RSP_CC:
        set_cost_connectivity_objective(m, conservation, connectivity)
    elif connectivity and connectivity.strategy == c.RSP_CON:
        set_connectivity_objective(m, conservation, connectivity)
    #elif conservation.strategy == c.RSP_BLM:
    #    set_cost_blm_objective(m, conservation, pux)
    elif conservation.strategy == c.RSP_CF or conservation.strategy == c.RSP:
        set_cost_objective(m, conservation)
    else:
        error = "Unknown strategy, objective can not be set"
        sys.exit(error)

    m.update()

###                                        ###
# Model initialization                       #
###                                        ###

def solve_model(m, timer):
    """
    Start the model timer, let Gurobi solve the model and stop the timer

    Parameters
    ----------
    m : Gurobi model
        Model in Gurobi environment
    timer : Timer
        Timer object containing start, end times and functions
    Returns
    -------
    None
    """

    timer.start_solver()
    m.optimize()
    # LP
    #m.relax()
    timer.stop()

def setup_model(m, conservation, connectivity=None):
    """
    Set model constraints and objective function depending on RSP variant

    Parameters
    ----------
    m : Gurobi model
        Model in Gurobi environment
    conservation : Conservation
        Conservation object (pu, features, pvf, strategy, bounds)
    connectivity : Connectivity
        Connectivity object (strategy, weight, complete_graph, target), can be None if RPS without connectivity
    Returns
    -------
    None
    """

    # set features consrtaints for all strategies
    print("setting features targets...")
    c_set_features_target(m, conservation)

    if connectivity:
        if connectivity.strategy == c.RSP_CF:
            c_set_metric_target(m, conservation, connectivity)
        #elif connectivity.strategy == c.RSP_CON or connectivity.strategy == 'con-blm':
        elif connectivity.strategy == c.RSP_CON:
            c_set_cost_target(m, conservation)

    # set objective
    print("setting objective...")
    set_objective(m, conservation, connectivity)

def init_pu_x(m, pu):
    """
    Initialize dataframe containing decision variables x for each pu

    Parameters
    ----------
    m : Gurobi model
        Model in Gurobi environment
    pu : Pandas DataFrame
        DataFrame containing all planning units [pu_id, pu_cost, xloc, yloc]

    Returns
    -------
    DataFrame containing all pu id's and decision variables x [pu_id, pu_x]
    """

    x = [None] * len(pu)
    for i in range(len(x)):
        x[i] = m.addVar(vtype=GRB.BINARY, name = "x_" + str(pu[c.PU_ID][i]))
        # LP
        #x[i] = m.addVar(vtype=GRB.CONTINUOUS, name = "x_" + str(pu[i]))
        m.addConstr(x[i] <= 1)
        m.addConstr(x[i] >= 0)

    pu['x'] = x
    m.update()
    return pu

def set_gurobi_params(m, args):
    """
    Set gurobi params according to provided arguments

    Parameters
    ----------
    m : Gurobi model
        Model in Gurobi environment
    args : Argparse namespace
        Contains all passed arguments.
    Returns
    -------
    None
    """

    if args.gurobi_log:
        m.setParam('LogFile', args.gurobi_log)

    if args.time_limit:
        m.setParam('TimeLimit', args.time_limit)

    if args.gurobi_threads:
        m.setParam('Threads', args.gurobi_threads)

    if args.gap:
        m.setParam('MIPGap', args.gap)


def init_and_solve_model(args, conservation, timer, connectivity=None):
    """
    Create ILP model, setup constraints, solve and analyze the model

    Parameters
    ----------
    args : Argparse namespace
        Contains all passed arguments.
    conservation : Conservation
        Conservation object (pu, features, pvf, strategy, bounds)
    timer : Timer
        Timer object containing start, end times and functions
    connectivity : Connectivity
        Connectivity object (strategy, weight, complete_graph, target), can be None if RSP without connectivity

    Returns
    -------
    SolutionArea
       SolutionArea object containing the id's of the selected pu's, obj value, gap and timer
    """

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
            #pux = init_pu_x(m, conservation.pu[c.PU_ID])
            init_pu_x(m, conservation.pu)
            print("setting up model...")
            setup_model(m, conservation, connectivity)
            print("solving model...")
            solve_model(m, timer)
            return process_solution(m, conservation, timer)

def run_rsp(args, path, features, pu, pvf, timer):
    (conservation, connectivity) = init_conservation_and_connectivity(args, path, features, pu, pvf)
    print("conservation created...")

    # init and solve model
    solution = init_and_solve_model(args, conservation, timer, connectivity)
    analyze_and_save_solution(args, conservation, solution, connectivity)

    cio.print_solution_stats(solution, conservation, timer)
