import pandas as pd
import networkx as nx
import conmetric

class ConData:

    def __init__(self, name=None):
        self.name = name
        self.matrix = None
        self.edgelist = None
        self.habitat_edgelist = None
        self.metrics = {}
        self.g = None

    def set_connectivity_matrix(self, con_matrix):
        self.matrix = con_matrix
        self.g = nx.from_pandas_adjacency(self.matrix, create_using=nx.DiGraph())

    def set_connectivity_edgelist(self, con_edgelist):
        self.edgelist = con_edgelist
        self.g = nx.from_pandas_edgelist(con_edgelist, 'id1', 'id2', 'value', create_using=nx.DiGraph())

    def set_connectivity_habitat_edgelist(self, con_habitat_edgelist):
        self.habitat_edgelist = con_habitat_edgelist.drop(labels='habitat', axis=1)
        self.habitat_edgelist = self.habitat_edgelist.loc[self.habitat_edgelist['value'] != 0].reset_index(drop=True)
        self.g = nx.from_pandas_edgelist(self.habitat_edgelist, 'id1', 'id2', 'value', create_using=nx.DiGraph())

    def set_connectivity_metrics(self, metric_type):
        self.metrics[metric_type] = conmetric.ConnectivityMetric(metric_type)
        self.metrics[metric_type].set_connectivity_metrics(self.g)

    def get_metric_values(self, name):
        return self.metrics[name].values

    def get_normalized_metric_values(self, name):
        metric_values = self.metrics[name].values
        if metric_values['value'].min() != metric_values['value'].max():
            norm_data = (metric_values['value'] - metric_values['value'].min())/(metric_values['value'].max() - metric_values['value'].min())
            return pd.DataFrame(list(zip(metric_values['pu'], norm_data)), columns = ['pu', 'value'])
        else:
            # TODO: all values are the same, assume they are normalized (otherwise div by 0 error)
            return self.metrics[name].values

    def get_metric(self, name):
        return self.metrics[name]

    def drop_smaller_value(self, name, threshold):
        self.metrics[name].drop_smaller(threshold)

    def drop_smaller_type(self, name, min_type):
        self.metrics[name].drop_smaller_type(min_type)

    def drop_greater_value(self, name, max_type):
        self.metrics[name].drop_greater(max_type)

    def set_values_to_one(self, name):
        self.metrics[name].set_values_to_one()
