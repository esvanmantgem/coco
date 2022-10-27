import argparse as ap
# TODO Fix this mess
def parse_args():
    parser = ap.ArgumentParser(description = "Cocoplan command line arguments.")
    parser.add_argument('-input', type=str, required=True, help='Folder containing the input files')
    parser.add_argument('-output', type=str, required=True, help='Folder to store result files in')
    parser.add_argument('-strategy', required=True, choices=['cf', 'sd',  'cost', 'cost-con', 'con',  'con-blm', 'cost-con-live'], help='Strategy to calculate the metric')
    parser.add_argument('-blm', type=float, help='The value of the Boundary Length Modifier')

    # conservation feature metric parsing options
    #if parser.parse_known_args()[0].strategy.lower().startswith('cf'):
    if parser.parse_known_args()[0].strategy.lower() == 'cf':
        parser.add_argument('-mc', action='store_true', help='Set all connecitivy metric values to 1')
        parser.add_argument('-metric', action='append', required=True, choices=['indegree', 'outdegree', 'betcent'], help='Which connectivity metric to use')
        # TODO: now no way to mix metric min/max type and metric min/max
        # threshold values (min and max) parser
        min_value_parser = parser.add_mutually_exclusive_group()
        min_value_parser.add_argument('-metric-min', action='append', type=float, help='Minimum value to use when discritzing metric')
        min_value_parser.add_argument('-metric-min-type', action='append',choices=['min', 'mean', 'median'], help='Minimum value to calculate when discritzing metric')
        max_value_parser = parser.add_mutually_exclusive_group()
        max_value_parser.add_argument('-metric-max', action='append', type=float, help='Maximum value to use when discritzing metric')
        max_value_parser.add_argument('-metric-max-type', action='append', choices=['max', 'mean', 'median'], help='Minimum value to calculate when discritzing metric')

        # metric arguments parser
        metric_parser = parser.add_mutually_exclusive_group(required=True)
        #metric_parser = parser.add_mutually_exclusive_group()
        metric_parser.add_argument('-metric-prop', type=float, help='minimal proportion of the total metric value to obtain')
        metric_parser.add_argument('-metric-target',type=float, help='minimal target of the metric to obtain')

        # connectivity data parser
        con_data_parser = parser.add_mutually_exclusive_group()
        con_data_parser.add_argument('--con-matrix', type=str, action='append', help='File containing the connectivity matrix')
        con_data_parser.add_argument('--con-edgelist', type=str, action='append', help='File containing the connectivity edgelist')
        con_data_parser.add_argument('--habitat-edgelist', type=str, action='append', help='File containing the connectivity habitat edgelist')

    # cost and metric optimization parsing options
    if parser.parse_known_args()[0].strategy.lower() == 'cost-con':
        parser.add_argument('-mc', action='store_true', help='Set all connecitivy metric values to 1')
        parser.add_argument('-metric', action='append', required=True, choices=['indegree', 'outdegree', 'betcent'], help='Which connectivity metric to use')
        parser.add_argument('-metric-weight',type=float, help='weight of the metric in the objectivve function')
        # TODO: now no way to mix metric min/max type and metric min/max
        # threshold values (min and max) parser
        min_value_parser = parser.add_mutually_exclusive_group()
        min_value_parser.add_argument('-metric-min', action='append', type=float, help='Minimum value to use when discritzing metric')
        min_value_parser.add_argument('-metric-min-type', action='append',choices=['min', 'mean', 'median'], help='Minimum value to calculate when discritzing metric')
        max_value_parser = parser.add_mutually_exclusive_group()
        max_value_parser.add_argument('-metric-max', action='append', type=float, help='Maximum value to use when discritzing metric')
        max_value_parser.add_argument('-metric-max-type', action='append', choices=['max', 'mean', 'median'], help='Minimum value to calculate when discritzing metric')

        # connectivity data parser
        con_data_parser = parser.add_mutually_exclusive_group()
        con_data_parser.add_argument('--con-matrix', type=str, action='append', help='File containing the connectivity matrix')
        con_data_parser.add_argument('--con-edgelist', type=str, action='append', help='File containing the connectivity edgelist')
        con_data_parser.add_argument('--habitat-edgelist', type=str, action='append', help='File containing the connectivity habitat edgelist')

    # live optimization
    if parser.parse_known_args()[0].strategy.lower() == 'cost-con-live':
        parser.add_argument('-mc', action='store_true', help='Set all connecitivy metric values to 1')
        parser.add_argument('-metric', action='append', required=True, choices=['indegree', 'outdegree', 'betcent'], help='Which connectivity metric to use')
        parser.add_argument('-metric-weight',type=float, help='weight of the metric in the objectivve function')
        # TODO: now no way to mix metric min/max type and metric min/max
        # threshold values (min and max) parser
        min_value_parser = parser.add_mutually_exclusive_group()
        min_value_parser.add_argument('-metric-min', action='append', type=float, help='Minimum value to use when discritzing metric')
        min_value_parser.add_argument('-metric-min-type', action='append',choices=['min', 'mean', 'median'], help='Minimum value to calculate when discritzing metric')
        max_value_parser = parser.add_mutually_exclusive_group()
        max_value_parser.add_argument('-metric-max', action='append', type=float, help='Maximum value to use when discritzing metric')
        max_value_parser.add_argument('-metric-max-type', action='append', choices=['max', 'mean', 'median'], help='Minimum value to calculate when discritzing metric')

        # connectivity data parser
        con_data_parser = parser.add_mutually_exclusive_group()
        con_data_parser.add_argument('--con-matrix', type=str, action='append', help='File containing the connectivity matrix')
        con_data_parser.add_argument('--con-edgelist', type=str, action='append', help='File containing the connectivity edgelist')
        con_data_parser.add_argument('--habitat-edgelist', type=str, action='append', help='File containing the connectivity habitat edgelist')

    # metric only optimization parsing options
    if parser.parse_known_args()[0].strategy.lower() == 'con':
        parser.add_argument('-mc', action='store_true', help='Set all connecitivy metric values to 1')
        parser.add_argument('-metric', action='append', required=True, choices=['indegree', 'outdegree', 'betcent'], help='Which connectivity metric to use')
        parser.add_argument('-max-cost',type=float, required=True, help='max cost of the conservation area')
        parser.add_argument('-min-cost',type=float, help='min cost of the conservation area')
        # TODO: now no way to mix metric min/max type and metric min/max
        # threshold values (min and max) parser
        min_value_parser = parser.add_mutually_exclusive_group()
        min_value_parser.add_argument('-metric-min', action='append', type=float, help='Minimum value to use when discritzing metric')
        min_value_parser.add_argument('-metric-min-type', action='append',choices=['min', 'mean', 'median'], help='Minimum value to calculate when discritzing metric')
        max_value_parser = parser.add_mutually_exclusive_group()
        max_value_parser.add_argument('-metric-max', action='append', type=float, help='Maximum value to use when discritzing metric')
        max_value_parser.add_argument('-metric-max-type', action='append', choices=['max', 'mean', 'median'], help='Minimum value to calculate when discritzing metric')

        # connectivity data parser
        con_data_parser = parser.add_mutually_exclusive_group()
        con_data_parser.add_argument('--con-matrix', type=str, action='append', help='File containing the connectivity matrix')
        con_data_parser.add_argument('--con-edgelist', type=str, action='append', help='File containing the connectivity edgelist')
        con_data_parser.add_argument('--habitat-edgelist', type=str, action='append', help='File containing the connectivity habitat edgelist')

    # metric only optimization parsing options
    if parser.parse_known_args()[0].strategy.lower() == 'con-blm':
        parser.add_argument('-mc', action='store_true', help='Set all connecitivy metric values to 1')
        parser.add_argument('-metric', action='append', required=True, choices=['indegree', 'outdegree', 'betcent'], help='Which connectivity metric to use')
        parser.add_argument('-max-cost',type=float, required=True, help='max cost of the conservation area')
        parser.add_argument('-min-cost',type=float, help='min cost of the conservation area')
        # TODO: now no way to mix metric min/max type and metric min/max
        # threshold values (min and max) parser
        min_value_parser = parser.add_mutually_exclusive_group()
        min_value_parser.add_argument('-metric-min', action='append', type=float, help='Minimum value to use when discritzing metric')
        min_value_parser.add_argument('-metric-min-type', action='append',choices=['min', 'mean', 'median'], help='Minimum value to calculate when discritzing metric')
        max_value_parser = parser.add_mutually_exclusive_group()
        max_value_parser.add_argument('-metric-max', action='append', type=float, help='Maximum value to use when discritzing metric')
        max_value_parser.add_argument('-metric-max-type', action='append', choices=['max', 'mean', 'median'], help='Minimum value to calculate when discritzing metric')

        # connectivity data parser
        con_data_parser = parser.add_mutually_exclusive_group()
        con_data_parser.add_argument('--con-matrix', type=str, action='append', help='File containing the connectivity matrix')
        con_data_parser.add_argument('--con-edgelist', type=str, action='append', help='File containing the connectivity edgelist')
        con_data_parser.add_argument('--habitat-edgelist', type=str, action='append', help='File containing the connectivity habitat edgelist')

    parser.add_argument('-gap', type=float, help='Set the allowed gap to the optimal')
    parser.add_argument('-time-limit', type=int, help='Time limit to restrict the runtime of Gurobi')
    parser.add_argument('-gurobi-log', type=str, help='File path to store Gurobi log in')
    parser.add_argument('-gurobi-threads', type=int, help='The number of threads to restrict Gurobi to')
    parser.add_argument('-gurobi-mem', type=float, help='The amount of memory (in GB) to restrict Gurobi to')
    return parser.parse_args()
