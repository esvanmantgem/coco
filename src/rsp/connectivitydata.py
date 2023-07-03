# Copyright (c) 2022, Eline van Mantgem
#
# This file is part of Coco.
#
# Coco is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Coco is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Coco.  If not, see <http://www.gnu.org/licenses/>.

import pandas as pd
import networkx as nx
import rsp.connectivitymetric as metric
import constant as c
import numpy as np

class ConnectivityData:

    def __init__(self, name=None):
        """
        Creates and initializes a new ConnectivityData object with name name if provided

        Parameters
        ----------
        name : str
            Name of the new ConnectivityData object

        Returns
        ----------
        None
        """

        self.name = name
        self.matrix = None
        self.edgelist = None
        self.feature_edgelist = None
        self.metrics = {}

    def set_connectivity_matrix(self, con_matrix, metrics, node_values):
        """
        Sets the connectivity matrix of the dataset and calculates the metrics on it

        Parameters
        ----------
        con_matrix : Pandas DataFrame
            Pandas DataFrame containing the connectivity matrix
        metrics : list
            List of strings with the names of the metrics
        node_values : Pandas DataFrame
            Pandas DataFrame containing the planning unit attribute values
        Returns
        -------
        None
        """

        self.matrix = con_matrix
        for metric_type in metrics:
            g = nx.from_pandas_adjacency(self.matrix, create_using=nx.DiGraph())
            self.set_connectivity_metrics(metric_type, g, node_values)

    def set_connectivity_edgelist(self, con_edgelist, metrics, node_values):
        """
        Sets the connectivity edgelist of the dataset and calculates the metrics on it

        Parameters
        ----------
        con_edgelist : Pandas DataFrame
            Pandas DataFrame containing the connectivity edgelist
        metrics : list
            List of strings with the names of the metrics
        node_values : Pandas DataFrame
            Pandas DataFrame containing the planning unit attribute values
        Returns
        -------
        None
        """

        self.edgelist = con_edgelist
        for metric_type in metrics:
            #TODO add betcent complete graph drop
            g = nx.from_pandas_edgelist(con_edgelist, c.HEL_PID1, c.HEL_PID2, c.HEL_VAL, create_using=nx.DiGraph())
            self.set_connectivity_metrics(metric_type, g, node_values)

    def set_connectivity_feature_edgelist(self, con_feature_edgelist, metrics, complete_graph, node_values):
        """
        Sets the (feature) edgelist of the dataset and calculates the metrics on it

        Parameters
        ----------
        con_feature_edgelist : Pandas DataFrame
            Pandas DataFrame containing the connectivity data
        metrics : list
            List of strings with the names of the metrics
        complete_graph : str
            A string containing the type of values to be dropped in case of a complete graph
        node_values : Pandas DataFrame
            Pandas DataFrame containing the planning unit attribute values
        Returns
        -------
        None
        """

        self.feature_edgelist = con_feature_edgelist.drop(labels=c.HEL_FID, axis=1)
        self.feature_edgelist = self.feature_edgelist.loc[self.feature_edgelist[c.HEL_VAL] != 0].reset_index(drop=True)
        for metric_type in metrics:
            # drop values under mean value for BC iff complete graph
    # Now: we drop LOW values (aka not the resistance values). This is implemented to use the same
    # edgeweights for BC dropping as for the EC probability of connectivity. This should be rewritten
    # to require 2 different datasets: 1.resistance values per edge for BC and 2.probability of connectivity of
    # each edge
    # SO: if you run with complete graph BC, run probability map. If you run with a none complete graph, it doesn't matter because we don't use the edge-weighted version
    # todo: implement edge weighted version for the BC optionally
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
        """
        Set the attribute values on the nodes of the connectivity graph

        Parameters
        ----------
        args : Argparse namespace
            Contains all passed arguments.

        Returns
        -------
        Pandas DataFrame containting all the arguments and corresponding values
        """
        ''' Set the node values for metrics that need it given in the planning unit attribute file '''
        node_values.drop(c.ATTR_FID, inplace=True, axis=1)
        node_attr = node_values.set_index(c.ATTR_PID).to_dict()[c.ATTR_VAL]
        nx.set_node_attributes(self.metrics[c.EC].g, node_attr, c.NODE_VAL)

    def set_connectivity_metrics(self, metric_type, g, node_values):
        """
        Initializes a new ConnectivityMetric object for the metric and calculates its values on graph g

        Parameters
        ----------
        metric_type : str
            Name of the metric
        g : Networkx Graph
            Graph the metric should be calculated on
        node_values : Pandas DataFrame
            DataFrame containing the planning unit attribute values (if needed)
        Returns
        -------
        None
        """

        self.metrics[metric_type] = metric.ConnectivityMetric(metric_type, g)
        if metric_type == c.EC and node_values is not None:
            self.set_node_values(node_values)
        self.metrics[metric_type].set_connectivity_metrics()

    #def set_connectivity_metrics(self, metric_type):
    #    print("set metric type: ", metric_type)
    #    self.metrics[metric_type] = conmetric.ConnectivityMetric(metric_type)
    #    self.metrics[metric_type].set_connectivity_metrics(self.g)

    def get_metric_values(self, name):
        """
        Returns the values of the Pandas DataFrame of metric name

        Parameters
        ----------
        name : str
            Name of the metric to get the values of

        Returns
        -------
        Pandas DataFrame containing all values of the metric per planning unit
        """

        return self.metrics[name].values

    def get_normalized_metric_values(self, name):
        """
        Calculates and returns the normalized values of the Pandas DataFrame of metric name

        Parameters
        ----------
        name : str
            Name of the metric to get the values of

        Returns
        -------
        Pandas DataFrame containing all normalized values of the metric per planning unit
        """

        metric_values = self.metrics[name].values

        if name == c.EC:
            return self.normalize_edge_weights(metric_values)
        elif name == c.BC or name == c.INDEG or name == c.OUTDEG:
            return self.normalize_node_weights(metric_values)
        else:
            error = "Metric unknown for normalization"
            sys.exit(error)

    def normalize_node_weights(self, metric_values):
        """
        Calculates and returns the normalized values of the Pandas Series of node metric name

        Parameters
        ----------
        metric_values : Pandas Series
            Metric values to get the values of

        Returns
        -------
        Pandas DataFrame containing all normalized values of the node metric per planning unit
        """

        if metric_values[c.MET_VAL].min() != metric_values[c.MET_VAL].max():
            norm_data = (metric_values[c.MET_VAL] - metric_values[c.MET_VAL].min())/(metric_values[c.MET_VAL].max() - metric_values[c.MET_VAL].min())
            return pd.DataFrame(list(zip(metric_values[c.MET_PID], norm_data)), columns = [c.MET_PID, c.MET_VAL])
        else:
            # TODO: all values are the same, assume they are normalized (otherwise div by 0 error)
            if metric_values[c.MET_VAL].min() > 0:
                print("Warning: no normalization needed, node min is equal to max, all values set to 1")
                vals = np.ones(len(metric_values.index))
            else:
                print("Warning: no normalization needed, all values are 0")
                vals = np.zeros(len(metric_values.index))
#df.loc[df['First Season'] > 1990, 'First Season'] = 1
            #metric_values.loc[metric_values[c.MET_VAL] > 0, c.MET_VAL] = 1

            return pd.DataFrame(list(zip(metric_values[c.MET_PID], vals )), columns = [c.MET_PID, c.MET_VAL])
            #return metric_values

    def normalize_edge_weights(self, metric_values):
        """
        Creates a new Pandas DataFrame containting all the arguments and corresponding values

        Parameters
        ----------
        metric_values : Pandas Series
            Metric values to get the values of

        Returns
        -------
        Pandas DataFrame containing all normalized values of the edge metric per planning unit pair
        """

        if metric_values[c.MET_VAL].min() != metric_values[c.MET_VAL].max():
            norm_data = (metric_values[c.MET_VAL] - metric_values[c.MET_VAL].min())/(metric_values[c.MET_VAL].max() - metric_values[c.MET_VAL].min())
            return pd.DataFrame(list(zip(metric_values[c.MET_PID1], metric_values[c.MET_PID2], norm_data)), columns = [c.MET_PID1,  c.MET_PID2, c.MET_VAL])
        else:
            # TODO: all values are the same, assume they are normalized (otherwise div by 0 error)
            print("Warning: no normalization needed, edge min is equal to max")
            if metric_values[c.MET_VAL].min() > 0:
                vals = np.ones(len(metric_values.index))
            else:
                vals = np.zeros(len(metric_values.index))
#df.loc[df['First Season'] > 1990, 'First Season'] = 1
            #metric_values.loc[metric_values[c.MET_VAL] > 0, c.MET_VAL] = 1

            return pd.DataFrame(list(zip(metric_values[c.MET_PID], vals )), columns = [c.MET_PID, c.MET_VAL])
            #return metrics_values

    def get_metric(self, name):
        """
        Returns the ConnectivityMetricMet object with name name

        Parameters
        ----------
        name : str
            Name of the metric to return

        Returns
        -------
        ConnectivityMetricMet object with name name
        """

        return self.metrics[name]

    def drop_smaller_value(self, name, threshold):
        """
        Drops all values for the metric below the threshold value of metric name

        Parameters
        ----------
        name : str
            Name of the metric
        threshold : float
            Threshold value to drop values below of

        Returns
        -------
        None
        """

        self.metrics[name].drop_smaller(threshold)

    def drop_smaller_type(self, name, min_type):
        """
        Drops all values for the metric below the threshold type of metric name

        Parameters
        ----------
        name : str
            Name of the metric
        min_type : str
            Threshold type to drop values below of

        Returns
        -------
        None
        """

        self.metrics[name].drop_smaller_type(min_type)

    def drop_greater_value(self, name, threshold):
        """
        Drops all values for the metric above the threshold value of metric name

        Parameters
        ----------
        name : str
            Name of the metric
        threshold : float
            Threshold value to drop values above of

        Returns
        -------
        None
        """

        self.metrics[name].drop_greater(threshold)

    def drop_greater_type(self, name, max_type):
        """
        Drops all values for all datasets above the threshold type of metric name

        Parameters
        ----------
        name : str
            Name of the metric
        max_type : str
            Threshold type to drop values above of

        Returns
        -------
        None
        """

        self.metrics[name].drop_greater_type(max_type)

    def set_values_to_one(self, name):
        """
        Sets all values of metric name to 1

        Parameters
        ----------
        name : str
            Name of the metric

        Returns
        -------
        None
        """
        self.metrics[name].set_values_to_one()
