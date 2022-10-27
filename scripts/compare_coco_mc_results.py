import pandas as pd
import networkx as nx
import argparse as ap
import errno, sys, os, pathlib

########################
#   Metric calculation #
########################
class Metric:
    def __init__(self, metric_type):
        self.metric_type = metric_type

    def betcent(self, gr):
        all_betcent = nx.betweenness_centrality(gr, normalized=False)
        #all_betcent = nx.betweenness_centrality(gr, normalized=True)
        #print(all_betcent_norm)
        temp_values = []
        for k,v in all_betcent.items():
            temp_values.append(v)
        return pd.DataFrame(list(zip(gr.nodes(), temp_values)), columns = ['pu', 'value'])

    def outdegree(self, gr):
        temp_values = []
        for unit in gr.nodes():
            temp_values.append(gr.out_degree(unit))
        return pd.DataFrame(list(zip(gr.nodes(), temp_values)), columns = ['pu', 'value'])

    def indegree(self, gr):
        temp_values = []
        for unit in gr.nodes():
            temp_values.append(gr.out_degree(unit))
        return pd.DataFrame(list(zip(gr.nodes(), temp_values)), columns = ['pu', 'value'])

    def set_connectivity_metrics(self, g):
        do = f"{self.metric_type}"
        if hasattr(self, do) and callable(func := getattr(self, do)):
            return func(g)
        else:
            error = "Error: metric not implemented"
            sys.exit(error)

def main():
    parser = ap.ArgumentParser(description = "Cocoplan command line arguments.")
    parser.add_argument('-mc', type=str, help='Folder containing the MC test results')
    parser.add_argument('-coco', type=str, help='Folder containing the Coco test results')
    parser.add_argument('-metric', required=True, choices=['indegree', 'outdegree', 'betcent'], help='Which connectivity metric to use')
    parser.add_argument('-condata', type=str, required=True, help='Folder containing the connectivity data')
    parser.add_argument('--c', action='store_true', help='File containing the Coco test is in src/output, overwrites test')

    args = parser.parse_args()

    mc_path = os.path.join(args.mc, 'connect_best.txt')
    #mc_path = 'input/connect_best.txt'
    if not args.c:
        coco_path = os.path.join(args.coco, 'solution.csv')
    else:
        coco_path = '../src/output/solution.csv'

    condata = args.condata
    #path = args.mcin
    mc_best = pd.read_csv(mc_path)
    co_best = pd.read_csv(coco_path)

    # For matrix
    dft = pd.read_csv(condata)
    if dft.columns.str.contains('^Unnamed:').any():
        dft = pd.read_csv(file, index_col=[0])
    dft.columns = dft.columns.astype(int)
    g = nx.from_pandas_adjacency(dft, create_using=nx.DiGraph())
    gc = nx.from_pandas_adjacency(dft, create_using=nx.DiGraph())
    gp = nx.from_pandas_adjacency(dft, create_using=nx.DiGraph())
    gcp = nx.from_pandas_adjacency(dft, create_using=nx.DiGraph())

    # For edgelist
    #con_habitat_edgelist = pd.read_csv(condata)
    #habitat_edgelist = con_habitat_edgelist.drop(labels='habitat', axis=1)
    #habitat_edgelist = habitat_edgelist.loc[habitat_edgelist['value'] != 0].reset_index(drop=True)

    # Create graphs
    #g = nx.from_pandas_edgelist(habitat_edgelist, 'id1', 'id2', 'value', create_using=nx.DiGraph())
    #gp = nx.from_pandas_edgelist(habitat_edgelist, 'id1', 'id2', 'value', create_using=nx.DiGraph())
    #gc = nx.from_pandas_edgelist(habitat_edgelist, 'id1', 'id2', 'value', create_using=nx.DiGraph())
    #gcp = nx.from_pandas_edgelist(habitat_edgelist, 'id1', 'id2', 'value', create_using=nx.DiGraph())

    m = Metric(args.metric)
    mc = Metric(args.metric)

    ########################
    #   MC calculation     #
    ########################

    #The following lines are for pre connectivity:
    values = m.set_connectivity_metrics(g)
    mc_best_m = mc_best.copy()
    values = values.merge(mc_best_m['solution'], left_on='pu', right_on=mc_best_m['planning_unit'])
    values = values[values['solution'] > 0]
    metric_sum = values['value'].sum()
    avg =  metric_sum / len(values)

    print("Marxan Connect Pre:")
    print("Nr of Nodes (Total cost): ", len(values), "")
    print("Metric total: ", metric_sum)
    print("Metric per node/cost: ", avg)

    #The following lines are for post connectivity:
    out_nodes = list(mc_best.loc[mc_best['solution'] == 0]['planning_unit'])
    in_nodes = list(mc_best.loc[mc_best['solution'] == 1]['planning_unit'])
    gp.remove_nodes_from(out_nodes)
    pvalues = mc.set_connectivity_metrics(gp)
    pmetric_sum = pvalues['value'].sum()
    pavg =  pmetric_sum / len(pvalues)

    print("\nMarxan Connect Post:")
    print("Nr of Nodes (Total cost): ", len(pvalues), "")
    print("Metric total: ", pmetric_sum)
    print("Metric per node/cost: ", pavg)

    ########################
    #   Coco calculation   #
    ########################

    # The following lines are for pre connectivity
    cvalues = mc.set_connectivity_metrics(gc)
    co_best_m = co_best.copy()
    cvalues = cvalues.merge(co_best_m['x'], left_on='pu', right_on=co_best_m['pu'])
    cvalues = cvalues[cvalues['x'] > 0]
    cmetric_sum = cvalues['value'].sum()
    cavg =  cmetric_sum / len(cvalues)

    print("\nCoco Pre:")
    print("Nr of Nodes (Total cost): ", len(cvalues), "")
    print("Metric total: ", cmetric_sum)
    print("Metric per node/cost: ", cavg)

    #The following lines are for post connectivity:
    cout_nodes = list(co_best.loc[co_best['x'] == 0]['pu'])
    cin_nodes = list(co_best.loc[co_best['x'] == 1]['pu'])
    gcp.remove_nodes_from(cout_nodes)
    cpvalues = mc.set_connectivity_metrics(gcp)
    cpmetric_sum = cpvalues['value'].sum()
    cpavg =  cpmetric_sum / len(cpvalues)

    print("\nCoco Post:")
    print("Nr of Nodes (Total cost): ", len(cpvalues), "")
    print("Metric total: ", cpmetric_sum)
    print("Metric per node/cost: ", cpavg)

if __name__ == '__main__':
    main()
