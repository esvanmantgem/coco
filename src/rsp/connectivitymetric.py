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
import sys

class ConnectivityMetric:

    def __init__(self, metric_type, g):
        """
        Creates and initializes a new ConnectivityMetric object

        Parameters
        ----------
        metric_type : str
            Name of the metric
        g : Networkx graph
            Graph of the underlying dataset

        Returns
        -------
        None
        """

        self.metric_type = metric_type
        self.g = g
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
        """
        Sets the standard values for the metric on the graph

        Parameters
        ----------
        -

        Returns
        -------
        None
        """

        self.sum = self.values[c.MET_VAL].sum()
        self.mean = self.values[c.MET_VAL].mean()
        self.median = self.values[c.MET_VAL].median()
        self.min = self.values[c.MET_VAL].min()
        self.max = self.values[c.MET_VAL].max()
        self.min_threshold = self.values[c.MET_VAL].min()
        self.max_threshold = self.values[c.MET_VAL].max()

    def set_target(self, target):
        """
        Sets the target to be reached during optimization of the RSP-CF

        Parameters
        ----------
        target : float
            Value of the target to be set

        Returns
        -------
        None
        """

        self.target = target

    def indegree(self):
        """
        Calculate the indegree value of each node in the graph and store this in self.values

        Parameters
        ----------
        -

        Returns
        -------
        None
        """

        print("--- calculating indegree values ---")
        temp_values = []
        for unit in self.g.nodes():
            temp_values.append(self.g.in_degree(unit))
        self.values = pd.DataFrame(list(zip(self.g.nodes(), temp_values)), columns = [c.MET_PID, c.MET_VAL])
        print(self.values)
        self.calculate_standards()

    def outdegree(self):
        """
        Calculate the outdegree value of each node in the graph and store this in self.values

        Parameters
        ----------
        -

        Returns
        -------
        None
        """

        print("--- calculating outdegree values ---")
        temp_values = []
        for unit in self.g.nodes():
            temp_values.append(self.g.out_degree(unit))
        self.values = pd.DataFrame(list(zip(self.g.nodes(), temp_values)), columns = [c.MET_PID, c.MET_VAL])
        print(self.values)
        self.calculate_standards()

    def bc(self):
        """
        Calculate the betweenness centrality of each node in the graph and store this in self.values

        Parameters
        ----------
        -

        Returns
        -------
        None
        """

        print("--- calculating BC values ---")
        all_betcent = nx.betweenness_centrality(self.g, normalized=False, weight=None)
        #all_betcent_norm = nx.betweenness_centrality(g, normalized=True)
        #print(all_betcent_norm)
        temp_values = []
        for k,v in all_betcent.items():
            temp_values.append(v)
        self.values = pd.DataFrame(list(zip(self.g.nodes(), temp_values)), columns = [c.MET_PID, c.MET_VAL])
        print(self.values)
        self.calculate_standards()

    def ec(self):
        """
        Calculate the EC metric: for each pair of pu (i.e., edge):
        for each node i: for each neighbor j: a_i * a_j * p_ij
        Where a_i is qualitative value of pu i and p_ij a quantification of the 1/distance between planning units i and j
        Stores a list of tuples (i, j, val) in self.values

        Parameters
        ----------
        -

        Returns
        -------
        None
        """

        print("---calculating EC values ---")

        i_s = []
        j_s = []
        vals = []
        for i, a_i in nx.get_node_attributes(self.g, c.NODE_VAL).items():
            for j in self.g.neighbors(i):
                a_j =  self.g.nodes[j][c.NODE_VAL]
                p_ij = self.g.edges[(i,j)][c.EDGE_VAL]
                val = a_i * a_j * p_ij
                i_s.append(i)
                j_s.append(j)
                vals.append(val)
        self.values = pd.DataFrame(list(zip(i_s, j_s, vals)), columns = [c.MET_PID1, c.MET_PID2, c.MET_VAL])
        print(self.values)
        # TODO check "for each map"
        self.calculate_standards()

    def set_connectivity_metrics(self):
        """
        General function to calculate the connectivity metric. Calculates the correct metric depending on self.name

        Parameters
        ----------
        -

        Returns
        -------
        None
        """

        do = f"{self.metric_type}"
        if hasattr(self, do) and callable(func := getattr(self, do)):
            return func()
        else:
            error = "Error: metric not implemented"
            sys.exit(error)

    def drop_smaller(self, threshold):
        """
        Drops all values below the threshold value of metric name

        Parameters
        ----------
        threshold : float
            Threshold value to drop values below of

        Returns
        -------
        None
        """

        self.min_threshold = threshold
        self.values[c.MET_VAL] = self.values[c.MET_VAL].where(self.values[c.MET_VAL] >= self.min_threshold, other=0)

    def drop_greater(self, threshold):
        """
        Drops all values above the threshold value of metric name

        Parameters
        ----------
        threshold : float
            Threshold value to drop values above of

        Returns
        -------
        None
        """

        self.max_theshold = threshold
        self.values[c.MET_VAL] = self.values[c.MET_VAL].where(self.values[c.MET_VAL] <= self.max_threshold, other=0)

    def drop_smaller_type(self, type_name):
        """
        Drops all values below the value of the threhold type of metric name

        Parameters
        ----------
        threshold : float
            Threshold value to drop values below of

        Returns
        -------
        None
        """

        self.min_threshold = self.get_type(type_name)
        self.values[c.MET_VAL] = self.values[c.MET_VAL].where(self.values[c.MET_VAL] >= self.min_threshold, other=0)

    def drop_greater_type(self, type_name):
        """
        Drops all values above the value of the threhold type of metric name

        Parameters
        ----------
        threshold : float
            Threshold value to drop values above of

        Returns
        -------
        None
        """

        self.max_threshold = self.get_type(type_name)
        self.values[c.MET_VAL] = self.values[c.MET_VAL].where(self.values[c.MET_VAL] <= self.max_threshold, other=0)

    def get_type(self, type_name):
        """
        Returns the value of the type_name

        Parameters
        ----------
        type_name : str
            Type of the value to return

        Returns
        -------
        Float value of the type_name
        """

        if type_name == c.MEAN:
            return self.mean
        elif type_name == c.MEDIAN:
            return self.median
        elif type_name == c.MIN:
            return self.min
        elif type_name == c.MAX:
            return self.max
        else:
            #shouldn't get here
            error = "Error: type unknown"
            sys.exit(error)

    def set_values_to_one(self):
        """
        Sets all values of the metric to 1 or 0

        Parameters
        ----------
        -

        Returns
        -------
        None
        """

        self.orig_values = self.values.copy()
        self.values[c.MET_VAL] = self.values[c.MET_VAL].where(self.values[c.MET_VAL] == 0, other=1)
