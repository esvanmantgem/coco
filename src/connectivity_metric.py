import pandas as pd
import networkx as nx

class ConnectivityMetric:

    def __init__(self, metric_type, data):
        self.metric_type = metric_type
        #self.all_values = self.set_connectivity_metrics()
        self.g = nx.from_pandas_adjacency(data, create_using=nx.DiGraph())
        #g = nx.from_pandas_edgelist(bounds, 'id1', 'id2', 'boundary', create_using=nx.DiGraph())
        #self.all_values = self.set_connectivity_metrics(list(data.columns.values))
        self.pu = list(data.columns.values)
        self.values = pd.DataFrame()
        self.mean = 0
        self.sum = 0
        self.mean = 0
        self.median = 0
        self.min = 0
        self.max = 0

    def calculate_standards(self):
        self.sum = self.values['value'].sum()
        self.mean = self.values['value'].mean()
        self.median = self.values['value'].median()
        self.min = self.values['value'].min()
        self.max = self.values['value'].max()


    def indegree(self):
        temp_values = []
        for unit in self.pu:
            temp_values.append(self.g.in_degree(unit))
        self.values = pd.DataFrame(list(zip(self.pu, temp_values)), columns = ['pu', 'value'])
        self.calculate_standards()

    def outdegree(self):
        temp_values = []
        for unit in self.pu:
            temp_values.append(self.g.out_degree(unit))
        self.values = pd.DataFrame(list(zip(self.pu, temp_values)), columns = ['pu', 'value'])
        self.calculate_standards()

    def betcent(self):
        all_betcent = nx.betweenness_centrality(self.g, normalized=True)
        temp_values = []
        #print(values)
        for k,v in all_betcent.items():
            temp_values.append(v)
        self.values = pd.DataFrame(list(zip(self.pu, temp_values)), columns = ['pu', 'value'])
        self.calculate_standards()

    #@staticmethod
    #def set_connectivity_metrics(self, pu):
    def set_connectivity_metrics(self):
        do = f"{self.metric_type}"
        if hasattr(self, do) and callable(func := getattr(self, do)):
            return func()
        else:
            error = "Error: metric not implemented"
            sys.exit(error)

    def drop_smaller(self, threshold):
        self.values = self.values[self.values['value'] > threshold]

    def drop_greater(self, threshold):
        self.values = self.values[self.values['value'] < threshold]

    def drop_smaller_type(self, type_name):
        threshold = self.get_type(type_name)
        self.values = self.values[self.values['value'] > threshold]

    def drop_greater_type(self, type_name):
        threshold = self.get_type(type_name)
        self.values = self.values[self.values['value'] < threshold]

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
        self.values = self.values.assign(value=1)
