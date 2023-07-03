import pandas as pd
import networkx as nx
import conmetric
import constant as c

class ConData:

    def __init__(self, name=None):
        self.name = name
        self.matrix = None
        self.edgelist = None
        self.feature_edgelist = None
        self.metrics = {}
        #self.g = None

    def set_connectivity_matrix(self, con_matrix, metrics, node_values):
        self.matrix = con_matrix
        for metric_type in metrics:
            g = nx.from_pandas_adjacency(self.matrix, create_using=nx.DiGraph())
            self.set_connectivity_metrics(metric_type, g, node_values)

    def set_connectivity_edgelist(self, con_edgelist, metrics, node_values):
        self.edgelist = con_edgelist
        for metric_type in metrics:
            g = nx.from_pandas_edgelist(con_edgelist, c.HEL_PID1, c.HEL_PID2, c.HEL_VAL, create_using=nx.DiGraph())
            self.set_connectivity_metrics(metric_type, g, node_values)

    # TODO complete graph for Betcent fix: now only median drop, create param to set variable
    # Now: we drop LOW values (aka not the resistance values). This is implemented to use the same
    # edgeweights for BC dropping as for the EC probability of connectivity. This should be rewritten
    # to require 2 different datasets: 1.resistance values per edge for BC and 2.probability of connectivity of
    # each edge
    def set_connectivity_feature_edgelist(self, con_feature_edgelist, metrics, complete_graph, node_values):
        self.feature_edgelist = con_feature_edgelist.drop(labels=c.HEL_FID, axis=1)
        self.feature_edgelist = self.feature_edgelist.loc[self.feature_edgelist[c.HEL_VAL] != 0].reset_index(drop=True)
        for metric_type in metrics:
            # drop values under mean value for BC iff complete graph
            if metric_type == c.BC and complete_graph:
                bet_list = self.feature_edgelist.copy()
                if complete_graph == c.MEAN:
                    bet_list[c.HEL_VAL] = bet_list[c.HEL_VAL].where(bet_list[c.HEL_VAL] >= bet_list[c.HEL_VAL].mean(), other=0)
                elif complete_graph == c.MEDIAN:
                    bet_list[c.HEL_VAL] = bet_list[c.HEL_VAL].where(bet_list[c.HEL_VAL] >= bet_list[c.HEL_VAL].median(), other=0)
                # dropping 0 values
                bet_list = bet_list.loc[(bet_list[c.HEL_VAL] > 0)]
                g = nx.from_pandas_edgelist(bet_list, c.HEL_PID1, c.HEL_PID2, c.HEL_VAL, create_using=nx.DiGraph())
            else:
                g = nx.from_pandas_edgelist(self.feature_edgelist, c.HEL_PID1, c.HEL_PID2, c.HEL_VAL, create_using=nx.DiGraph())
            self.set_connectivity_metrics(metric_type, g, node_values)

    def set_node_values(self, node_values):
        ''' Set the node values for metrics that need it given in the planning unit attribue file '''
        node_values.drop(c.ATTR_FID, inplace=True, axis=1)
        node_attr = node_values.set_index(c.ATTR_PID).to_dict()[c.ATTR_VAL]
        nx.set_node_attributes(self.metrics[c.EC].g, node_attr, c.NODE_VAL)

    def set_connectivity_metrics(self, metric_type, g, node_values):
        #print("set metric type: ", metric_type)
        self.metrics[metric_type] = conmetric.ConnectivityMetric(metric_type, g)
        if metric_type == c.EC and node_values is not None:
            self.set_node_values(node_values)
        self.metrics[metric_type].set_connectivity_metrics()

    #def set_connectivity_metrics(self, metric_type):
    #    print("set metric type: ", metric_type)
    #    self.metrics[metric_type] = conmetric.ConnectivityMetric(metric_type)
    #    self.metrics[metric_type].set_connectivity_metrics(self.g)

    def get_metric_values(self, name):
        return self.metrics[name].values

    def get_normalized_metric_values(self, name):
        metric_values = self.metrics[name].values
        if metric_values[c.MET_VAL].min() != metric_values[c.MET_VAL].max():
            norm_data = (metric_values[c.MET_VAL] - metric_values[c.MET_VAL].min())/(metric_values[c.MET_VAL].max() - metric_values[c.MET_VAL].min())
            return pd.DataFrame(list(zip(metric_values[c.MET_PID], norm_data)), columns = [c.MET_PID, c.MET_VAL])
        else:
            # TODO: all values are the same, assume they are normalized (otherwise div by 0 error)
            return self.metrics[name].values

    def get_metric(self, name):
        return self.metrics[name]

    def drop_smaller_value(self, name, threshold):
        self.metrics[name].drop_smaller(threshold)

    def drop_smaller_type(self, name, min_type):
        self.metrics[name].drop_smaller_type(min_type)

    def drop_greater_value(self, name, threshold):
        self.metrics[name].drop_greater(threshold)

    def drop_greater_type(self, name, max_type):
        self.metrics[name].drop_greater_type(max_type)

    def set_values_to_one(self, name):
        self.metrics[name].set_values_to_one()
