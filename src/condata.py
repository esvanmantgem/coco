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
        #self.g = None

    def set_connectivity_matrix(self, con_matrix, metrics, node_values):
        self.matrix = con_matrix
        for metric_type in metrics:
            g = nx.from_pandas_adjacency(self.matrix, create_using=nx.DiGraph())
            self.set_connectivity_metrics(metric_type, g, node_values)

    def set_connectivity_edgelist(self, con_edgelist, metrics, node_values):
        self.edgelist = con_edgelist
        for metric_type in metrics:
            g = nx.from_pandas_edgelist(con_edgelist, 'id1', 'id2', 'value', create_using=nx.DiGraph())
            self.set_connectivity_metrics(metric_type, g, node_values)

    # TODO complete graph for Betcent fix: now only median drop, create param to set variable
    def set_connectivity_habitat_edgelist(self, con_habitat_edgelist, metrics, complete_graph, node_values):
        self.habitat_edgelist = con_habitat_edgelist.drop(labels='habitat', axis=1)
        self.habitat_edgelist = self.habitat_edgelist.loc[self.habitat_edgelist['value'] != 0].reset_index(drop=True)
        for metric_type in metrics:
            if metric_type == 'betcent' and complete_graph:
                bet_list = self.habitat_edgelist.copy()

                bet_list['value'] = bet_list['value'].where(bet_list['value'] >= bet_list['value'].mean(), other=0)
                bet_list = bet_list.loc[(bet_list['value']>0)]
                #df.loc[~(df==0).all(axis=1)]
                #print(bet_list)
                g = nx.from_pandas_edgelist(bet_list, 'id1', 'id2', 'value', create_using=nx.DiGraph())
            else:
                g = nx.from_pandas_edgelist(self.habitat_edgelist, 'id1', 'id2', 'value', create_using=nx.DiGraph())
            self.set_connectivity_metrics(metric_type, g, node_values)

    def set_node_values(self, node_values):
        print(node_values)
        node_values.drop('habitat', inplace=True, axis=1)
        node_attr = node_values.set_index('pu').to_dict()['amount']
        nx.set_node_attributes(self.metrics["ec"].g, node_attr, "value")

    #def set_pu_data(self, pu_data):
    #    if (self.g == None):
    #        print("Error no graph set")
    #        exit(0)
    #    else:
    #        pu_data.drop('habitat', inplace=True, axis=1)
    #        node_attr = pu_data.set_index('pu').to_dict()['amount']
    #        nx.set_node_attributes(self.g, node_attr, "value")

    def set_connectivity_metrics(self, metric_type, g, node_values):
        #print("set metric type: ", metric_type)
        self.metrics[metric_type] = conmetric.ConnectivityMetric(metric_type, g)
        if metric_type == "ec" and node_values is not None:
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

    def drop_greater_value(self, name, threshold):
        self.metrics[name].drop_greater(threshold)

    def drop_greater_type(self, name, max_type):
        self.metrics[name].drop_greater_type(max_type)

    def set_values_to_one(self, name):
        self.metrics[name].set_values_to_one()
