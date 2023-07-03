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
import seaborn as sns
import os
import matplotlib.pyplot as plt
import constant as c
import rsp.connectivitymetric as conMet

class SolutionArea:

    def __init__(self, pux, obj_val, gap, timer):
        """
        Creates and initializes a new SolutionArea object

        Parameters
        ----------
        pux : Pandas DataFrame
            DataFrame containing each planning unit and its decision variable
        obj_val : float
            Float indicating the objective value of the solution
        gap : float
            Float indicating the gap of this solution to the optimal solution
        timer : Timer
            Timer object containing all timers of the executed run

        Returns
        -------
        None
        """
        self.pux = pux
        self.obj_val = obj_val
        self.metrics_total = pd.DataFrame()
        self.features_total = pd.DataFrame()
        self.timer = timer
        self.gap = gap

    def save_run_stats(self, conservation):
        """
        Sets and returns all run statistics

        Parameters
        ----------
        conservation : Conservation
            Conservation containing the information for the runstats

        Returns
        -------
        A Pandas DataFrame [names, values] with all runstats
        """

        solver_time = self.timer.solver_time()
        total_time = self.timer.setup_time()

        values = [solver_time, total_time, self.obj_val, self.gap, self.total_cost(conservation)]
        names = [c.SOLVER_TIME, c.TOTAL_TIME, c.OBJ_VAL, c.GAP_OPT, c.TOTAL_COST]
        return pd.DataFrame(list(zip(names, values)), columns = [c.RUNSTAT_NAME, c.RUNSTAT_VAL])

    def features_sum(self, conservation):
        """
        Collects all data on features of this run and stores it in a DataFrame

        Parameters
        ----------
        conservation : Conservation
            Conservation containing the information for the runstats

        Returns
        -------
        A Pandas DataFrame [features, total, target, reached] of all features during this run
        """

        pvf = conservation.pvf
        temp = self.pux.merge(pvf, on=c.PUX_PID, how='left')
        pu_per_sp = [y for x, y in temp.groupby(c.PVF_FID)]

        spec = []
        total = []
        target = []
        reached = []

        for sp in pu_per_sp:
            s = int(sp[c.PVF_FID].iloc[-1])
            if conservation.has_target(s):
                spec.append(s)
                total.append(sp[c.PVF_VAL].sum())
                reached.append(sp.loc[sp[c.PUX_X] == 1, c.PVF_VAL].sum())
                if conservation.prop_target is not None:
                    t = conservation.prop_target.loc[conservation.prop_target[c.FEAT_ID] == s, c.FEAT_TARGET].item()
                else:
                    t = conservation.features.loc[conservation.features[c.FEAT_ID] == s, c.FEAT_TARGET].item()
                target.append(t)
        data = { c.FEATURES: spec, c.TOTAL_F: total, c.TARGET_F: target, c.REACHED_F: reached }
        self.features_total = pd.DataFrame(data)
        print(self.features_total)
        return self.features_total

    def print_metric_values(self, metric):
        """
        Prints the metric values of metric

        Parameters
        ----------
        metric : ConnectivityMetric
            Metric to print the values of

        Returns
        -------
        None
        """

        print()
        print("Sum of metric value: ", metric.sum)
        print("Mean of metric value: ", metric.mean)
        print("Median of metric value: ", metric.median)
        print("Min of metric value: ", metric.min)
        print("Max of metric value: ", metric.max)

    def metrics_sum(self, connectivity):
        """
        Collects all data on all metrics of this run and stores it in a DataFrame

        Parameters
        ----------
        connectivity : Connectivity
            Connecitivty object containing all metrics and data

        Returns
        -------
        A Pandas DataFrame with all information of all metrics on each dataset during this run
        """

        name = []
        min_value = []
        max_value = []
        min_threshold = []
        max_threshold = []
        total = []
        target = []
        reached = []
        #post_metric = []
        avg_per_node = []
        data_name = []

        for condata in connectivity.connectivity_data:
            for metric_name in condata.metrics:
                data_name.append(condata.name)
                metric = condata.get_metric(metric_name)
                min_value.append(metric.min)
                max_value.append(metric.max)
                min_threshold.append(metric.min_threshold)
                max_threshold.append(metric.max_threshold)
                total.append(metric.sum)
                name.append(metric_name)
                target.append(metric.target)
                #post_conn = self.analyze_post_connectivity(metric_name, condata)
                #post_metric.append(post_conn.sum())
                #avg = post_conn.sum() / len(post_conn)
                conn = self.analyze_connectivity(metric_name, condata, self.pux.copy())
                avg = conn.sum() / len(conn)
                reached.append(conn.sum())
                avg_per_node.append(avg)
        self.metrics_total = pd.DataFrame(list(zip(data_name, name, total, min_value, max_value, min_threshold, max_threshold, target, reached, avg_per_node)), columns = [c.DATA_M, c.METRIC_M, c.TOTAL_M, c.MIN_M, c.MAX_M, c.MIN_THRES, c.MAX_THRES, c.TARGET_M, c.TOTAL_METRIC_M, c.AVG_PER_PU])
        return self.metrics_total

    def total_cost(self, conservation):
        """
        Calculates the total cost of the conservation area

        Parameters
        ----------
        conservation : Conservation
            Conservation containing the information for the runstats

        Returns
        -------
        A float with the total cost of the conservation area
        """

        temp_pux = self.pux.merge(conservation.pu[c.PU_COST], left_on=c.PUX_PID, right_on=conservation.pu[c.PU_ID], how='left')
        return temp_pux.loc[temp_pux[c.PUX_X] == 1, c.PU_COST].sum()

    def analyze_post_connectivity(self, metric_name, connectivity):
        """
        Calculates the metric value of metric_name on the solution area

        Parameters
        ----------
        connectivity : Connectivity
            Connecitivty object containing all metrics and data
        metric_name : str
            Name of the metric to calculate

        Returns
        -------
        The values of the metric on the solution area
        """

        metric = connectivity.get_metric(metric_name)
        g = connectivity.g
        out_nodes = list(self.pux.loc[self.pux[c.PUX_X] == 0][c.PUX_PID])
        g.remove_nodes_from(out_nodes)
        sol_metric = ConnectivityMetric(metric_name)
        sol_metric.g = g
        sol_metric.set_connectivity_metrics(sol_metric.g)

        return sol_metric.values[c.MET_VAL]

    def analyze_connectivity(self, metric_name, condata, co_best):
        """
        Calculates the metric value of metric_name on a dataset

        Parameters
        ----------
        metric_name : str
            Name of the metric to calculate
        condata : ConnecitivtyData
            Dataset to calculate the metric on
        co_best : Pandas DataFrame
            DataFrame containing all values of the planning units

        Returns
        -------
        The values of the metric on the dataset
        """

        if metric_name == c.EC:
            metric = condata.get_metric(metric_name)
            print(metric.metric_type)
            sol_metric = conMet.ConnectivityMetric(metric_name, metric.g)

            sol_metric.set_connectivity_metrics()
            co_best = co_best[co_best[c.PUX_X] > 0]
            cvalues = sol_metric.values.merge(co_best[c.PUX_X], left_on=c.MET_PID1, right_on=co_best[c.PUX_PID])
            cvalues.rename(columns={c.PUX_X: 'x1'}, inplace=True)
            cvalues = cvalues.merge(co_best[c.PUX_X], left_on=c.MET_PID2, right_on=co_best[c.PUX_PID])
            cvalues.rename(columns={'x': 'x2'}, inplace=True)
            return cvalues[c.MET_VAL]
        else:
            metric = condata.get_metric(metric_name)
            sol_metric = conMet.ConnectivityMetric(metric_name, metric.g)
            sol_metric.set_connectivity_metrics()
            cvalues = sol_metric.values.merge(co_best[c.PUX_X], left_on=c.MET_PID, right_on=co_best[c.PUX_PID])
            cvalues = cvalues[cvalues[c.PUX_X] > 0]
            return cvalues[c.MET_VAL]

    def show_map(self, path):
        """
        Creates, plots and stores a visual map of the solution area

        Parameters
        ----------
        path : str
            Path to store the map

        Returns
        -------
        None
        """
        # plot map
        #ax1 = self.pux.plot.scatter(x='xloc', y='yloc', c='x', colormap='viridis')
        #plt.savefig('output/conservation.pdf', bbox_inches='tight')

        sns.scatterplot(data=self.pux, x=c.PU_XLOC, y=c.PU_YLOC, hue=c.PUX_X)
        #plt.legend(labels = ['not selected', 'selected'], title='Conservation area', loc='upper right', frameon=False)
        #plt.legend(labels = ['not selected', 'selected'])
        legend = plt.legend()
        legend.get_texts()[0].set_text('not selected')
        legend.get_texts()[1].set_text('selected')
        #file.to_csv(os.path.join(path,name), index=False)
        name = c.SOL_AREA
        #plt.savefig(os.path.join(path,name), bbox_inches='tight')
        plt.show()
