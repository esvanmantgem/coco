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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Coco. If not, see <http://www.gnu.org/licenses/>.

import pandas as pd
import networkx as nx
import constant as c
import rsp.connectivitymetric as metric
import rsp.connectivitydata as cdata

class Connectivity:

    def __init__(self, strategy, weight, complete_graph, target=False):
        """
        Creates and initializes a new Connectivity object

        Parameters
        ----------
        strategy : str
            The RSP variant
        weight : float
            Weight of the connectivity values in the objective function
        complete_graph : str
            The type of values that need to be dropped in case of a complete graph
        target : boolean
            Boolean indicating a target or proportion value
        Returns
        -------
        None
        """

        self.strategy = strategy
        self.weight = weight
        self.cost_weight = 1
        # target is boolean flag: true if target setting, false if proportion setting
        self.target = target
        self.connectivity_data = []
        self.metrics = []
        self.complete_graph = complete_graph

    def get_connectivity_data(self):
        """
        Returns the connectivity data

        Parameters
        ----------
        -

        Returns
        -------
        Returns the connectivity data
        """

        return self.connectivity_data

    #def set_metrics(self, metrics):
    #    """
    #    Creates a new Pandas DataFrame containting all the arguments and corresponding values

    #    Parameters
    #    ----------
    #    args : Argparse namespace
    #        Contains all passed arguments.

    #    Returns
    #    -------
    #    Pandas DataFrame containting all the arguments and corresponding values
    #    """
    #    for metric in metrics:
    #        self.metrics.append(metric)
    #        for data in self.connectivity_data:
    #            data.set_connectivity_metrics(metric)

    def set_connectivity_matrix(self, matrix, name, metrics, pu_data):
        """
        Initializes a new ConnectivityData object with the values of matrix

        Parameters
        ----------
        matrix : Pandas DataFrame
            DataFrame containing the connectivity information
        name : str
            Name of the dataset
        metrics : list
            List of strings containing all metrics to be set on the data
        pu_data : Pandas DataFrame
            DataFrame containing the planning unit attribute data (or None if not needed)
        Returns
        -------
        None
        """

        temp_data = cdata.ConnectivityData(name)
        temp_data.set_connectivity_matrix(matrix, metrics, pu_data)
        self.connectivity_data.append(temp_data)
        self.metrics = metrics

    #TODO check if this works
    def set_connectivity_edgelist(self, edgelist, name, metrics, pu_data):
        """
        Initializes a new ConnectivityData object with the values of edgelist

        Parameters
        ----------
        edgelist : Pandas DataFrame
            DataFrame containing the connectivity information
        name : str
            Name of the dataset
        metrics : list
            List of strings containing all metrics to be set on the data
        pu_data : Pandas DataFrame
            DataFrame containing the planning unit attribute data (or None if not needed)
        Returns
        -------
        None
        """

        temp_data = cdata.ConnectivityData(name)
        temp_data.set_connectivity_edgelist(edgelist, metrics, pu_data)
        self.connectivity_data.append(temp_data)
        self.metrics = metrics

    #def set_feature_connectivity_edgelist(self, edgelist, metrics, pu_data, conservation):
    def set_feature_connectivity_edgelist(self, edgelist, metrics, pu_data, conservation):
        """
        Initializes new ConnectivityData objects for each feature in edgelist

        Parameters
        ----------
        edgelist : Pandas DataFrame
            DataFrame containing the connectivity information
        metrics : list
            List of strings containing all metrics to be set on the data
        pu_data : Pandas DataFrame
            DataFrame containing the planning unit attribute data (or None if not needed)
        Returns
        -------
        None
        """

        feature = [y for x, y in edgelist.groupby(c.HEL_FID)]
        for h in feature:
            if (conservation.has_target(h[c.PVF_FID].iloc[-1])):
                #target = conservation.get_target(feature[c.PVF_FID].iloc[-1])
                #if conservation.has_target(h.iloc[feature][-1])
                nh = pd.DataFrame(h).reset_index(drop=True)
                name = nh[c.HEL_FID][0]
                temp_data = cdata.ConnectivityData(name)
                node_data = None if pu_data is None else self.find_pu_data(pu_data, name)
                temp_data.set_connectivity_feature_edgelist(h, metrics, self.complete_graph, node_data)
                self.connectivity_data.append(temp_data)
        self.metrics = metrics

    def find_pu_data(self, pu_data, hab_find):
        """
        Finds the feature hab_find in the pu_data DataFrame and returs all entries with that feature

        Parameters
        ----------
        pu_data : Pandas DataFrame
            DataFrame containing all planning unit attribute data
        hab_find : str
            Name of the feature to find the attribute data on
        Returns
        -------
        Pandas DataFrame containting all entries in pu_data concerning feature hab_find
        """

        feature = [y for x, y in pu_data.groupby(c.ATTR_FID)]
        for h in feature:
            nh = pd.DataFrame(h).reset_index(drop=True)
            name = nh[c.ATTR_FID][0]
            if name == hab_find:
                return h
        return None

    #def get_condata(self, name):
    #    """
    #    Creates a new Pandas DataFrame containting all the arguments and corresponding values

    #    Parameters
    #    ----------
    #    args : Argparse namespace
    #        Contains all passed arguments.

    #    Returns
    #    -------
    #    Pandas DataFrame containting all the arguments and corresponding values
    #    """
    #    for data in self.connectivity_data:
    #        if data.name == name:
    #            return data
    #    nData = condata.ConData(name)
    #    self.connectivity_data.append(nData)
    #    return nData

    #def get_metric_values(self, name):
    #    """
    #    Returns a list of all metric values of metric name

    #    Parameters
    #    ----------
    #    name : str
    #        The name of the metric type to get

    #    Returns
    #    -------
    #    Returns a list of all the metric values of metric name for all datasets
    #    """

    #    metrics = []
    #    for data in self.connectivity_data:
    #        metrics.append(data.get_metric_values(name))
    #    return metrics

    #def get_normalized_metric_values(self, name):
    #    """
    #    Creates a new Pandas DataFrame containting all the arguments and corresponding values

    #    Parameters
    #    ----------
    #    args : Argparse namespace
    #        Contains all passed arguments.

    #    Returns
    #    -------
    #    Pandas DataFrame containting all the arguments and corresponding values
    #    """
    #    metrics = []
    #    for data in self.connectivity_data:
    #        metric_values = data.get_metric_values(name)
    #        normalized_data = (metric_values[c.MET_VAL] - metric_values[c.MET_VAL].min())/(metric_values[c.MET_VAL].max() - metric_values[c.MET_VAL].min())
    #        metrics.append(normalized_data)
    #    return metrics

    #TODOL check this method
    #def get_metric(self, name):
    #    """
    #    Creates a new Pandas DataFrame containting all the arguments and corresponding values

    #    Parameters
    #    ----------
    #    args : Argparse namespace
    #        Contains all passed arguments.

    #    Returns
    #    -------
    #    Pandas DataFrame containting all the arguments and corresponding values
    #    """
    #    metrics = []
    #    for data in self.connectivity_data:
    #        return data.get_metric(name)
    #    return metrics

    def drop_smaller_value(self, name, threshold):
        """
        Drops all values for all dataset below the threshold value of metric name

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

        for data in self.connectivity_data:
            data.drop_smaller_value(name, threshold)

    def drop_smaller_type(self, name, min_type):
        """
        Drops all values for all datasets below the threshold type of metric name

        Parameters
        ----------
        name : str
            Name of the metric
        threshold : str
            Threshold type to drop values below of
        Returns
        -------
        None
        """
        for data in self.connectivity_data:
            data.drop_smaller_type(name, min_type)

    def drop_greater_value(self, name, threshold):
        """
        Drops all values for all datasets above the threshold value of metric name

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

        for data in self.connectivity_data:
            data.drop_greater(name, threshold)

    def drop_greater_type(self, name, max_type):
        """
        Drops all values for all datasets above the threshold type of metric name

        Parameters
        ----------
        name : str
            Name of the metric
        threshold : str
            Threshold type to drop values above of
        Returns
        -------
        None
        """

        for data in self.connectivity_data:
            data.drop_greater_type(name, max_type)

    def set_values_to_one(self, name):
        """
        Sets all values for all datasets of metric name to 1

        Parameters
        ----------
        name : str
            Name of the metric

        Returns
        -------
        None
        """

        for data in self.connectivity_data:
            data.set_values_to_one(name)
