import pandas as pd
import networkx as nx
import conmetric
import condata

class Connectivity:

    def __init__(self, strategy, weight, target=False):
        self.strategy = strategy
        self.weight = weight
        # target is boolean flag: true if target setting, false if proportion setting
        self.target = target
        self.connectivity_data = []

    #def __init__(self, strategy, weight, target):
    #    self.strategy = strategy
    #    self.weight = weight
    #    # target is boolean flag: true if target setting, false if proportion setting
    #    self.target = target
    #    self.connectivity_data = []

    def get_connectivity_data(self):
        return self.connectivity_data

    def set_metric(self, metric_type):
        for data in self.connectivity_data:
            data.set_connectivity_metrics(metric_type)

    def set_connectivity_matrix(self, matrix, name):
        temp_data = condata.ConData(name)
        temp_data.set_connectivity_matrix(matrix)
        self.connectivity_data.append(temp_data)

    #TODO check if this works
    def set_connectivity_edgelist(self, edgelist, name):
        temp_data = condata.ConData(name)
        temp_data.set_connectivity_edgelist(edgelist)
        self.connectivity_data.append(temp_data)

    def set_habitat_connectivity_edgelist(self, edgelist):
        habitat = [y for x, y in edgelist.groupby('habitat')]
        for h in habitat:
            nh = pd.DataFrame(h).reset_index(drop=True)
            name = nh['habitat'][0]
            temp_data = condata.ConData(name)
            temp_data.set_connectivity_habitat_edgelist(h)
            self.connectivity_data.append(temp_data)

    def get_metric_values(self, name):
        metrics = []
        for data in self.connectivity_data:
            metrics.append(data.get_metric_values(name))
        return metrics

    def get_normalized_metric_values(self, name):
        metrics = []
        for data in self.connectivity_data:
            metric_values = data.get_metric_values(name)
            normalized_data = (metric_values['value'] - metric_values['value'].min())/(metric_values['value'].max() - metric_values['value'].min())
            metrics.append(normalized_data)
        return metrics

    def get_metric(self, name):
        metrics = []
        for data in self.connectivity_data:
            return data.get_metric(name)
        return metrics

    def drop_smaller_value(self, name, threshold):
        for data in self.connectivity_data:
            data.drop_smaller_value(name, threshold)

    def drop_smaller_type(self, name, min_type):
        for data in self.connectivity_data:
            data.drop_smaller_type(name, min_type)

    def drop_greater_value(self, name, max_type):
        for data in self.connectivity_data:
            data.drop_greater(name, max_type)

    def set_values_to_one(self, name):
        for data in self.connectivity_data:
            data.set_values_to_one(name)
