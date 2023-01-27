import argparse

LICENSE = """
Copyright (C) Eline van Mantgem
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
Coco is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.\n
"""

def parse_args():

    coco_parser = argparse.ArgumentParser(add_help=False)
    coco_parser.add_argument('--gap', type=float, help='Set the allowed gap to the optimal')
    coco_parser.add_argument('--time-limit', type=int, help='Time limit to restrict the runtime of Gurobi')
    coco_parser.add_argument('--gurobi-log', type=str, help='File path to store Gurobi log in')
    coco_parser.add_argument('--gurobi-threads', type=int, help='The number of threads to restrict Gurobi to')
    coco_parser.add_argument('--gurobi-mem', type=float, help='The amount of memory (in GB) to restrict Gurobi to')

    parser = argparse.ArgumentParser("Coco", formatter_class=argparse.RawTextHelpFormatter, description="Finding optimal solutions to variations of the RSP including connectivity")


    subparsers = parser.add_subparsers(title='Coco subcommands', dest='cmd', description='for specific help on RSP variants use: python coco.py {cmd} --help')

    ###
    # RSP-CF parser
    ###
    cf = subparsers.add_parser("RSP-CF", parents=[coco_parser])
    cf.add_argument('--input', type=str, required=True, help='Folder containing the input files')
    cf.add_argument('--output', type=str, required=True, help='Folder to store result files in')
    cf.add_argument('--metric', action='append', required=True, choices=['ec', 'indegree', 'outdegree', 'bc'], help='Which connectivity metric to use')

    # metric arguments parser
    cf_metric = cf.add_mutually_exclusive_group(required=True)
    cf_metric.add_argument('--metric-prop', type=float, help='minimal proportion of the total metric value to obtain')
    cf_metric.add_argument('--metric-target',type=float, help='minimal target of the metric to obtain')

    cf_min = cf.add_mutually_exclusive_group()
    cf_min.add_argument('--metric-min', action='append', type=float, help='Minimum value to use when discritzing metric')
    cf_min.add_argument('--metric-min-type', action='append',choices=['min', 'mean', 'median'], help='Minimum value to calculate when discritzing metric')
    cf_max = cf.add_mutually_exclusive_group()
    cf_max.add_argument('--metric-max', action='append', type=float, help='Maximum value to use when discritzing metric')
    cf_max.add_argument('--metric-max-type', action='append', choices=['max', 'mean', 'median'], help='Minimum value to calculate when discritzing metric')

    cf_con_data = cf.add_mutually_exclusive_group(required=True)
    cf_con_data.add_argument('--con-matrix', type=str, action='append', help='File containing the connectivity matrix')
    cf_con_data.add_argument('--con-edgelist', type=str, action='append', help='File containing the connectivity edgelist')
    cf_con_data.add_argument('--feature-edgelist', type=str, action='append', help='File containing the connectivity edgelist for different features')
    cf.add_argument('--pu-data', type=str, help='File containing attribute values for planning units per feature')

    #cf.add_argument('--complete-graph', action='store_true', help='Indicates the data contains a complete graph')
    cf.add_argument('--complete-graph', choices=['mean', 'median'], help='Indicates the data contains a complete graph, all values below should be dropped')

    ###
    # RSP-CC parser
    ###
    cc = subparsers.add_parser("RSP-CC", parents=[coco_parser])
    cc.add_argument('--input', type=str, required=True, help='Folder containing the input files')
    cc.add_argument('--output', type=str, required=True, help='Folder to store result files in')
    cc.add_argument('--metric', action='append', required=True, choices=['ec', 'indegree', 'outdegree', 'bc'], help='Which connectivity metric to use')
    cc.add_argument('--metric-weight',type=float, required=True, help='weight of the metric in the objectivve function')
    cc.add_argument('--cost-weight',type=float, help='weight of the metric in the objectivve function')

    cc_min = cc.add_mutually_exclusive_group()
    cc_min.add_argument('--metric-min', action='append', type=float, help='Minimum value to use when discritzing metric')
    cc_min.add_argument('--metric-min-type', action='append',choices=['min', 'mean', 'median'], help='Minimum value to calculate when discritzing metric')
    cc_max = cc.add_mutually_exclusive_group()
    cc_max.add_argument('--metric-max', action='append', type=float, help='Maximum value to use when discritzing metric')
    cc_max.add_argument('--metric-max-type', action='append', choices=['max', 'mean', 'median'], help='Minimum value to calculate when discritzing metric')

    cc_con_data = cc.add_mutually_exclusive_group(required=True)
    cc_con_data.add_argument('--con-matrix', type=str, action='append', help='File containing the connectivity matrix')
    cc_con_data.add_argument('--con-edgelist', type=str, action='append', help='File containing the connectivity edgelist')
    cc_con_data.add_argument('--feature-edgelist', type=str, action='append', help='File containing the connectivity feature edgelist')
    cc.add_argument('--pu-data', type=str, help='File containing attribute values for planning units per feature')

    #cc.add_argument('--complete-graph', action='store_true', help='Indicates the data contains a complete graph')
    #cc.add_argument('--complete-graph', action='store_true', help='Indicates the data contains a complete graph')
    cc.add_argument('--complete-graph', choices=['mean', 'median'], help='Indicates the data contains a complete graph, all values below should be dropped')

    ###
    # RSP-Con parser
    ###
    con = subparsers.add_parser("RSP-Con", parents=[coco_parser])
    con.add_argument('--input', type=str, required=True, help='Folder containing the input files')
    con.add_argument('--output', type=str, required=True, help='Folder to store result files in')
    con.add_argument('--metric', action='append', required=True, choices=['ec', 'indegree', 'outdegree', 'bc'], help='Which connectivity metric to use')
    con.add_argument('--max-cost',type=float, required=True, help='max cost of the conservation area')
    con.add_argument('--min-cost',type=float, help='min cost of the conservation area')

    con_min = con.add_mutually_exclusive_group()
    con_min.add_argument('--metric-min', action='append', type=float, help='Minimum value to use when discritzing metric')
    con_min.add_argument('--metric-min-type', action='append',choices=['min', 'mean', 'median'], help='Minimum value to calculate when discritzing metric')
    con_max = con.add_mutually_exclusive_group()
    con_max.add_argument('--metric-max', action='append', type=float, help='Maximum value to use when discritzing metric')
    con_max.add_argument('--metric-max-type', action='append', choices=['max', 'mean', 'median'], help='Minimum value to calculate when discritzing metric')

    con_data = con.add_mutually_exclusive_group(required=True)
    con_data.add_argument('--con-matrix', type=str, action='append', help='File containing the connectivity matrix')
    con_data.add_argument('--con-edgelist', type=str, action='append', help='File containing the connectivity edgelist')
    con_data.add_argument('--feature-edgelist', type=str, action='append', help='File containing the connectivity feature edgelist')
    con.add_argument('--pu-data', type=str, help='File containing attribute values for planning units per feature')

    #con.add_argument('--complete-graph', action='store_true', help='Indicates the data contains a complete graph')
    con.add_argument('--complete-graph', choices=['mean', 'median'], help='Indicates the data contains a complete graph, all values below should be dropped')

    ###
    # RSP-BLM parser
    ###
    #blm = subparsers.add_parser("RSP-BLM", parents=[coco_parser])
    #blm.add_argument('--blm-weight',type=float, help='weight of the blm in the objectivve function')
    #blm.add_argument('--input', type=str, required=True, help='Folder containing the input files')
    #blm.add_argument('--output', type=str, required=True, help='Folder to store result files in')

    ###
    # RSP parser
    ###
    cost = subparsers.add_parser("RSP", parents=[coco_parser])
    cost.add_argument('--input', type=str, required=True, help='Folder containing the input files')
    cost.add_argument('--output', type=str, required=True, help='Folder to store result files in')

    return parser.parse_args()

