import pandas as pd
import networkx as nx
import sys

class ConnectivityMetric:

    def __init__(self, metric_type):
        self.metric_type = metric_type
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

    def indegree(self, g):
        temp_values = []
        for unit in g.nodes():
            temp_values.append(g.in_degree(unit))
        self.values = pd.DataFrame(list(zip(g.nodes(), temp_values)), columns = ['pu', 'value'])
        self.calculate_standards()

    def outdegree(self, g):
        temp_values = []
        for unit in g.nodes():
            temp_values.append(g.out_degree(unit))
        self.values = pd.DataFrame(list(zip(g.nodes(), temp_values)), columns = ['pu', 'value'])
        self.calculate_standards()

    def betcent(self, g):
        all_betcent = nx.betweenness_centrality(g, normalized=False)
        #all_betcent_norm = nx.betweenness_centrality(g, normalized=True)
        #print(all_betcent_norm)
        temp_values = []
        for k,v in all_betcent.items():
            temp_values.append(v)
        self.values = pd.DataFrame(list(zip(g.nodes(), temp_values)), columns = ['pu', 'value'])
        self.calculate_standards()

    def set_connectivity_metrics(self, g):
        do = f"{self.metric_type}"
        if hasattr(self, do) and callable(func := getattr(self, do)):
            return func(g)
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
