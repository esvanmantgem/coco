import pandas as pd
import networkx as nx
import constant as c
import sys

class ConnectivityMetric:

    def __init__(self, metric_type, g):
        self.metric_type = metric_type
        self.g = g
        self.values = pd.DataFrame()
        self.mean = 0
        self.sum = 0
        self.mean = 0
        self.median = 0
        self.min = 0
        self.max = 0
        self.target = 0
        self.min_threshold = 0
        self.max_threshold = 0
        self.orig_values = None

    def calculate_standards(self):
        self.sum = self.values[c.MET_VAL].sum()
        self.mean = self.values[c.MET_VAL].mean()
        self.median = self.values[c.MET_VAL].median()
        self.min = self.values[c.MET_VAL].min()
        self.max = self.values[c.MET_VAL].max()
        self.min_threshold = self.values[c.MET_VAL].min()
        self.max_threshold = self.values[c.MET_VAL].max()

    def set_target(self, target):
        self.target = target

    def indegree(self):
        print("--- calculating indegree values ---")
        temp_values = []
        for unit in self.g.nodes():
            temp_values.append(self.g.in_degree(unit))
        self.values = pd.DataFrame(list(zip(self.g.nodes(), temp_values)), columns = [c.MET_PID, c.MET_VAL])
        print(self.values)
        self.calculate_standards()

    def outdegree(self):
        print("--- calculating outdegree values ---")
        temp_values = []
        for unit in self.g.nodes():
            temp_values.append(self.g.out_degree(unit))
        self.values = pd.DataFrame(list(zip(self.g.nodes(), temp_values)), columns = [c.MET_PID, c.MET_VAL])
        print(self.values)
        self.calculate_standards()

    def bc(self):
        print("--- calculating BC values ---")
        all_betcent = nx.betweenness_centrality(self.g, normalized=False, weight=None)
        #all_betcent_norm = nx.betweenness_centrality(g, normalized=True)
        #print(all_betcent_norm)
        temp_values = []
        for k,v in all_betcent.items():
            temp_values.append(v)
        self.values = pd.DataFrame(list(zip(self.g.nodes(), temp_values)), columns = [c.MET_PID, c.MET_VAL])
        print(self.values)
        self.calculate_standards()

    def ec(self):
        print("---calculating EC values ---")
        '''Calculate the EC metric: for each pair of pu (i.e., edge):
        for each node i: for each neighbor j: a_i * a_j * p_ij
        Where a_i is qualitative value of pu i and p_ij a quantification of the
        1/distance between planning units i and j

        Returns a list of tuples (i, j, val)
        '''

        i_s = []
        j_s = []
        vals = []
        for i, a_i in nx.get_node_attributes(self.g, c.NODE_VAL).items():
            for j in self.g.neighbors(i):
                a_j =  self.g.nodes[j][c.NODE_VAL]
                p_ij = self.g.edges[(i,j)][c.EDGE_VAL]
                val = a_i * a_j * p_ij
                i_s.append(i)
                j_s.append(j)
                vals.append(val)
        self.values = pd.DataFrame(list(zip(i_s, j_s, vals)), columns = [c.MET_PID1, c.MET_PID2, c.MET_VAL])
        print(self.values)
        # TODO check "for each map"
        self.calculate_standards()

    def set_connectivity_metrics(self):
        do = f"{self.metric_type}"
        if hasattr(self, do) and callable(func := getattr(self, do)):
            return func()
        else:
            error = "Error: metric not implemented"
            sys.exit(error)

    def drop_smaller(self, threshold):
        self.min_threshold = threshold
        self.values[c.MET_VAL] = self.values[c.MET_VAL].where(self.values[c.MET_VAL] >= self.min_threshold, other=0)

    def drop_greater(self, threshold):
        self.max_theshold = threshold
        self.values[c.MET_VAL] = self.values[c.MET_VAL].where(self.values[c.MET_VAL] <= self.max_threshold, other=0)

    def drop_smaller_type(self, type_name):
        self.min_threshold = self.get_type(type_name)
        self.values[c.MET_VAL] = self.values[c.MET_VAL].where(self.values[c.MET_VAL] >= self.min_threshold, other=0)

    def drop_greater_type(self, type_name):
        self.max_threshold = self.get_type(type_name)
        self.values[c.MET_VAL] = self.values[c.MET_VAL].where(self.values[c.MET_VAL] <= self.max_threshold, other=0)

    def get_type(self, type_name):
        if type_name == c.MEAN:
            return self.mean
        elif type_name == c.MEDIAN:
            return self.median
        elif type_name == c.MIN:
            return self.min
        elif type_name == c.MAX:
            return self.max
        else:
            #shouldn't get here
            error = "Error: type unknown"
            sys.exit(error)

    def set_values_to_one(self):
        self.orig_values = self.values.copy()
        self.values[c.MET_VAL] = self.values[c.MET_VAL].where(self.values[c.MET_VAL] == 0, other=1)
