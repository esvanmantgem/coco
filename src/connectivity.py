import pandas as pd
import networkx as nx
import conmetric
import condata

class Connectivity:

    def __init__(self, strategy, weight, complete_graph, target=False):
        self.strategy = strategy
        self.weight = weight
        self.cost_weight = 1
        # target is boolean flag: true if target setting, false if proportion setting
        self.target = target
        self.connectivity_data = []
        self.metrics = []
        self.complete_graph = complete_graph

    #def __init__(self, strategy, weight, target):
    #    self.strategy = strategy
    #    self.weight = weight
    #    # target is boolean flag: true if target setting, false if proportion setting
    #    self.target = target
    #    self.connectivity_data = []

    def get_connectivity_data(self):
        return self.connectivity_data

    def set_metrics(self, metrics):
        for metric in metrics:
            self.metrics.append(metric)
            for data in self.connectivity_data:
            #print("for data: ", data.name)
                data.set_connectivity_metrics(metric)

    def set_connectivity_matrix(self, matrix, name, metrics, pu_data):
        temp_data = condata.ConData(name)
        temp_data.set_connectivity_matrix(matrix, metrics, pu_data)
        self.connectivity_data.append(temp_data)
        #self.set_metrics(metrics)
        self.metrics = metrics

    #TODO check if this works
    def set_connectivity_edgelist(self, edgelist, name, metrics, pu_data):
        temp_data = condata.ConData(name)
        temp_data.set_connectivity_edgelist(edgelist, metrics, pu_data)
        self.connectivity_data.append(temp_data)
        self.metrics = metrics

    def set_habitat_connectivity_edgelist(self, edgelist, metrics, pu_data):
        habitat = [y for x, y in edgelist.groupby('habitat')]
        for h in habitat:
            nh = pd.DataFrame(h).reset_index(drop=True)
            name = nh['habitat'][0]
            temp_data = condata.ConData(name)
            node_data = None if pu_data is None else self.set_pu_data(pu_data, name)
            temp_data.set_connectivity_habitat_edgelist(h, metrics, self.complete_graph, node_data)
            self.connectivity_data.append(temp_data)
        self.metrics = metrics

    def set_pu_data(self, pu_data, hab_find):
        habitat = [y for x, y in pu_data.groupby('habitat')]
        for h in habitat:
            nh = pd.DataFrame(h).reset_index(drop=True)
            name = nh['habitat'][0]
            if name == hab_find:
                return h
        return None
            #nh = pd.DataFrame(h).reset_index(drop=True)
            #name = nh['habitat'][0]
            #condata = self.get_condata(name)
            #condata.set_pu_data(h)

    def get_condata(self, name):
        for data in self.connectivity_data:
            if data.name == name:
                return data
        nData = condata.ConData(name)
        self.connectivity_data.append(nData)
        return nData

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

    #TODOL check this method
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

    def drop_greater_value(self, name, threshold):
        for data in self.connectivity_data:
            data.drop_greater(name, threshold)

    def drop_greater_type(self, name, max_type):
        for data in self.connectivity_data:
            data.drop_greater_type(name, max_type)

    def set_values_to_one(self, name):
        for data in self.connectivity_data:
            data.set_values_to_one(name)
