import pandas as pd
import networkx as nx
from connectivity_metric import *

# TODO fix this class. Not very nice like this. Works though
class Connectivity:

    #def __init__(self, metric_type, strategy, weight, target, threshold_min, threshold_max, mc, con_data):
    def __init__(self, strategy, weight, target, con_data):
        self.strategy = strategy
        #self.metric_type = m_type
        self.weight = weight
        self.target = target
        self.con_data = con_data
        self.metrics = {}

    def add_metric(self, metric_type):
        self.metrics[metric_type] = ConnectivityMetric(metric_type, self.con_data)
        self.metrics[metric_type].set_connectivity_metrics()

    def get_metric_values(self, name):
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
#    def sum(self):
#        return self.all_values['value'].sum()
#
#    def mean(self):
#        return self.all_values['value'].mean()
#
#    def median(self):
#        return self.all_values['value'].median()
#
#    def indegree(self, pu, g):
#        pu_id = []
#        values = []
#        total_pu = []
#        total_values = []
#        for unit in pu['id']:
#            in_deg = g.in_degree(unit)
#            # No target set, use weighted values
#            if self.threshold_min is None and self.threshold_max is None:
#                values.append(in_deg)
#                pu_id.append(unit)
#            # Only max threshold set
#            elif self.threshold_min is None:
#                if in_deg < self.threshold_max:
#                    values.append(1)
#                    pu_id.append(unit)
#            # Only min threshold set
#            else:
#                if in_deg > self.threshold_min:
#                    values.append(1)
#                    pu_id.append(unit)
#            total_values.append(in_deg)
#            total_pu.append(pu_id)
#
#            #pu_id.append(unit)
#        #for node in g:
#        #    pu.append(node)
#        #    values.append(g.in_degree(node))
#        self.all_values = pd.DataFrame(list(zip(total_pu, total_values)), columns = ['pu', 'value'])
#        return pd.DataFrame(list(zip(pu_id, values)), columns = ['pu', 'value'])
#
#    def outdegree(self, pu, g):
#        pu = []
#        values = []
#        for node in g:
#            pu.append(node)
#            values.append(g.out_degree(node))
#        return pd.DataFrame(list(zip(pu, values)), columns = ['pu', 'value'])
#
#    def betcent(self, pu, g):
#        pu_id = []
#        value = []
#        values = nx.betweenness_centrality(g, normalized=True)
#        total_pu = []
#        total_values = []
#        #print(values)
#        for k,v in values.items():
#            if self.threshold_min is None and self.threshold_max is None:
#                value.append(v)
#                pu_id.append(k)
#            # Only max threshold set
#            elif self.threshold_min is None:
#                if v < self.threshold_max:
#                    value.append(1)
#                    pu_id.append(k)
#            # Only min threshold set
#            else:
#                if v > self.threshold_min:
#                    value.append(1)
#                    pu_id.append(k)
#            #pu.append(k)
#            #value.append(v)
#            total_values.append(v)
#            total_pu.append(k)
#
#        self.all_values = pd.DataFrame(list(zip(total_pu, total_values)), columns = ['pu', 'value'])
#        return pd.DataFrame(list(zip(pu_id, value)), columns = ['pu', 'value'])
#
#    #@staticmethod
#    def get_connectivity_metrics(self, pu, g):
#        do = f"{self.m_type}"
#        if hasattr(self, do) and callable(func := getattr(self, do)):
#            return func(pu, g)
#        else:
#            error = "Error: metric not implemented"
#            sys.exit(error)
