import pandas as pd
import networkx as nx
import seaborn as sns
import os
import matplotlib.pyplot as plt
import constant as c
from conmetric import *

class SolutionArea:

    def __init__(self, pux, obj_val, gap, timer):
        self.pux = pux
        self.obj_val = obj_val
        self.metrics_total = pd.DataFrame()
        self.features_total = pd.DataFrame()
        self.timer = timer
        self.gap = gap

    def save_run_stats(self, conservation):
        solver_time = self.timer.solver_time()
        total_time = self.timer.setup_time()

        values = [solver_time, total_time, self.obj_val, self.gap, self.total_cost(conservation)]
        names = [c.SOLVER_TIME, c.TOTAL_TIME, c.OBJ_VAL, c.GAP_OPT, c.TOTAL_COST]
        return pd.DataFrame(list(zip(names, values)), columns = [c.RUNSTAT_NAME, c.RUNSTAT_VAL])

    # pvf: features, pu, amount
    def features_sum(self, conservation):
        pvf = conservation.pvf
        temp = self.pux.merge(pvf, on=c.PUX_PID, how='left')
        pu_per_sp = [y for x, y in temp.groupby(c.PVF_FID)]

        spec = []
        total = []
        target = []
        reached = []

        for sp in pu_per_sp:
            s = int(sp[c.PVF_FID].iloc[-1])
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
        print("solutionsnnnnnnnnnnn")
        print(data)
        print(self.features_total)
        return self.features_total

    def print_metric_values(self, metric):
        print()
        print("Sum of metric value: ", metric.sum)
        print("Mean of metric value: ", metric.mean)
        print("Median of metric value: ", metric.median)
        print("Min of metric value: ", metric.min)
        print("Max of metric value: ", metric.max)

    def metrics_sum(self, connectivity):
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

        #print(data.g.nodes.data('value'))
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
        temp_pux = self.pux.merge(conservation.pu[c.PU_COST], left_on=c.PUX_PID, right_on=conservation.pu[c.PU_ID], how='left')
        return temp_pux.loc[temp_pux[c.PUX_X] == 1, c.PU_COST].sum()

    def analyze_post_connectivity(self, metric_name, connectivity):
        metric = connectivity.get_metric(metric_name)
        g = connectivity.g
        out_nodes = list(self.pux.loc[self.pux[c.PUX_X] == 0][c.PUX_PID])
        g.remove_nodes_from(out_nodes)
        sol_metric = ConnectivityMetric(metric_name)
        sol_metric.g = g
        sol_metric.set_connectivity_metrics(sol_metric.g)

        return sol_metric.values[c.MET_VAL]

    def analyze_connectivity(self, metric_name, condata, co_best):

        if metric_name == c.EC:
            metric = condata.get_metric(metric_name)
            print(metric.metric_type)
            sol_metric = ConnectivityMetric(metric_name, metric.g)

            sol_metric.set_connectivity_metrics()
            co_best = co_best[co_best[c.PUX_X] > 0]
            cvalues = sol_metric.values.merge(co_best[c.PUX_X], left_on=c.MET_PID1, right_on=co_best[c.PUX_PID])
            cvalues.rename(columns={c.PUX_X: 'x1'}, inplace=True)
            cvalues = cvalues.merge(co_best[c.PUX_X], left_on=c.MET_PID2, right_on=co_best[c.PUX_PID])
            cvalues.rename(columns={'x': 'x2'}, inplace=True)
            return cvalues[c.MET_VAL]
        else:

            metric = connectivity.get_metric(metric_name)
            g = connectivity.g
            sol_metric = ConnectivityMetric(metric_name)
            sol_metric.g = g
            sol_metric.set_connectivity_metrics(sol_metric.g)

            #metric = condata.get_metric(metric_name)
            #sol_metric = ConnectivityMetric(metric_name, metric.g)
            #sol_metric.set_connectivity_metrics()

            cvalues = sol_metric.values.merge(co_best[c.PUX_X], left_on=c.MET_PID, right_on=co_best[c.PUX_PID])
            cvalues = cvalues[cvalues[c.PUX_X] > 0]
            return cvalues[c.MET_VAL]

    def show_map(self, path):
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
        plt.savefig(os.path.join(path,name), bbox_inches='tight')
        plt.show()
