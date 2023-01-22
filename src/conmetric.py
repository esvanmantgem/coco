import pandas as pd
import networkx as nx
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
        self.sum = self.values['value'].sum()
        self.mean = self.values['value'].mean()
        self.median = self.values['value'].median()
        self.min = self.values['value'].min()
        self.max = self.values['value'].max()
        self.min_threshold = self.values['value'].min()
        self.max_threshold = self.values['value'].max()

    def set_target(self, target):
        self.target = target

    def indegree(self):
        print("------------calcuting indegree values -----------------")
        temp_values = []
        for unit in self.g.nodes():
            temp_values.append(self.g.in_degree(unit))
        self.values = pd.DataFrame(list(zip(self.g.nodes(), temp_values)), columns = ['pu', 'value'])
        print(self.values)
        self.calculate_standards()

    def outdegree(self):
        print("------------calcuting outdegree values -----------------")
        temp_values = []
        for unit in self.g.nodes():
            temp_values.append(self.g.out_degree(unit))
        self.values = pd.DataFrame(list(zip(self.g.nodes(), temp_values)), columns = ['pu', 'value'])
        print(self.values)
        self.calculate_standards()

    def betcent(self):
        print("------------calcuting betcent values -----------------")
        all_betcent = nx.betweenness_centrality(self.g, normalized=False, weight=None)
        #all_betcent_norm = nx.betweenness_centrality(g, normalized=True)
        #print(all_betcent_norm)
        temp_values = []
        for k,v in all_betcent.items():
            print(k ,v)
            temp_values.append(v)
        self.values = pd.DataFrame(list(zip(self.g.nodes(), temp_values)), columns = ['pu', 'value'])
        #print(self.values)
        self.calculate_standards()

    def ec(self):
        print("------------calcuting EC values -----------------")
        '''Calculate the EC metric: for each pair of pu (i.e., edge):
        for each node i: for each neighbor j: a_i * a_j * p_ij
        Where a_i is qualitative value of pu i and p_ij a quantification of the
        1/distance between planning units i and j

        Returns a list of tuples (i, j, val)
        '''

        i_s = []
        j_s = []
        vals = []
        for i, a_i in nx.get_node_attributes(self.g, "value").items():
            for j in self.g.neighbors(i):
                a_j =  self.g.nodes[j]["value"]
                p_ij = self.g.edges[(i,j)]["value"]
                val = a_i * a_j * p_ij
                i_s.append(i)
                j_s.append(j)
                vals.append(val)
        self.values = pd.DataFrame(list(zip(i_s, j_s, vals)), columns = ['pu1', 'pu2', 'value'])
        print(self.values)
        # TODO check "for each map"
        self.calculate_standards()
#        print(self.values['value'])
#for neighbor in G.neighbors(x):
#    print(G.nodes[neighbor]["time"])
        #for node, weight in nx.get_edge_attributes(g, "value"):
        #    print("node: ", node, " has weight ", weight)
        #    for n, k in g.neighbors(node):
        #        print(n, k)
        #print(nx.get_node_attributes(g, "value"))
#        for edge, weight in nx.get_edge_attributes(g, "value").items():
#            print("edge:", edge)
#            print("weight:", weight)

    def set_connectivity_metrics(self):
        do = f"{self.metric_type}"
        if hasattr(self, do) and callable(func := getattr(self, do)):
            return func()
        else:
            error = "Error: metric not implemented"
            sys.exit(error)

    def drop_smaller(self, threshold):
        self.min_threshold = threshold
        self.values['value'] = self.values['value'].where(self.values['value'] >= self.min_threshold, other=0)
        #self.values = self.values[self.values['value'] >= threshold]

    def drop_greater(self, threshold):
        self.max_theshold = threshold
        #self.values = self.values[self.values['value'] <= threshold]
        self.values['value'] = self.values['value'].where(self.values['value'] <= self.max_threshold, other=0)

    def drop_smaller_type(self, type_name):
        self.min_threshold = self.get_type(type_name)
        #self.values = self.values[self.values['value'] >= self.min_threshold]
        #sdf[cols2] = df[cols2].where(df[cols]<=0.9, other=0)
        self.values['value'] = self.values['value'].where(self.values['value'] >= self.min_threshold, other=0)
        #ou can use df.where(cond, other) to replace the values with other where cond == False.
        #print(self.values)

    def drop_greater_type(self, type_name):
        self.max_threshold = self.get_type(type_name)
        self.values['value'] = self.values['value'].where(self.values['value'] <= self.max_threshold, other=0)
        #self.values = self.values[self.values['value'] <= self.max_threshold]

    def get_type(self, type_name):
        if type_name == 'mean':
            return self.mean
        elif type_name == 'median':
            return self.median
        elif type_name == 'min':
            return self.min
        elif type_name == 'max':
            return self.max
        else:
            #shouldn't get here
            return None

    def set_values_to_one(self):
        self.orig_values = self.values.copy()
        self.values['value'] = self.values['value'].where(self.values['value'] == 0, other=1)
