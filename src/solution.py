import pandas as pd
import networkx as nx
import seaborn as sns
import os
import matplotlib.pyplot as plt
from conmetric import *

class SolutionArea:

    def __init__(self, pux, obj_val, gap, timer):
        self.pux = pux
        self.obj_val = obj_val
        self.metrics_total = pd.DataFrame()
        self.species_total = pd.DataFrame()
        self.timer = timer
        self.gap = gap

    def save_run_stats(self, conservation):
        solver_time = self.timer.solver_time()
        total_time = self.timer.setup_time()

        values = [solver_time, total_time, self.obj_val, self.gap, self.total_cost(conservation)]
        names = ['solver time', 'total time', 'objective value', 'gap-to-opt', 'total cost']
        return pd.DataFrame(list(zip(names, values)), columns = ['name', 'value'])

    # puvspr: species, pu, amount
    def species_sum(self, conservation):
        puvspr = conservation.puvspr
        temp = self.pux.merge(puvspr, on='pu', how='left')
        pu_per_sp = [y for x, y in temp.groupby('species')]

        spec = []
        total = []
        target = []
        reached = []

        for sp in pu_per_sp:
            s = int(sp['species'].iloc[-1])
            spec.append(s)
            total.append(sp['amount'].sum())
            reached.append(sp.loc[sp['x'] == 1, 'amount'].sum())
            if conservation.prop_target is not None:
                t = conservation.prop_target.loc[conservation.prop_target['id'] == s, 'target'].item()
            else:
                t = conservation.species.loc[conservation.species['id'] == s, 'target'].item()
            target.append(t)
        data = { "species": spec, "total": total, "target": target, "reached": reached }
        self.species_total = pd.DataFrame(data)
        return self.species_total

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
            print("condata: ", condata.name)
            for metric_name in condata.metrics:
                print("metric: ", metric_name)
                data_name.append(condata.name)
                metric = condata.get_metric(metric_name)
                print(condata.name, " is next, with metric: ", metric_name)
                #self.print_metric_values(metric)
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
                print("\n", condata.name, "\nMetric: ", metric_name, "\nTotal:", metric.sum, "\nTarget:", metric.target, "\nTotal metric:", conn.sum(), "\nAvg per pu:", avg)
        self.metrics_total = pd.DataFrame(list(zip(data_name, name, total, min_value, max_value, min_threshold, max_threshold, target, reached, avg_per_node)), columns = ['data', 'metric', 'total', 'min', 'max', 'min_threshold', 'max_threshold', 'target', 'total_metric', 'avg_per_pu'])
        return self.metrics_total

        #for condata in connectivity.connectivity_data:
        #    for metric_name in condata.metrics:
        #        data_name.append(condata.name)
        #        metric = condata.get_metric(metric_name)
        #        self.print_metric_values(metric)
        #        min_value.append(metric.min)
        #        max_value.append(metric.max)
        #        min_threshold.append(metric.min_threshold)
        #        max_threshold.append(metric.max_threshold)
        #        total.append(metric.sum)
        #        name.append(metric_name)
        #        target.append(metric.target)
        #        #post_conn = self.analyze_post_connectivity(metric_name, condata)
        #        #post_metric.append(post_conn.sum())
        #        #avg = post_conn.sum() / len(post_conn)
        #        conn = self.analyze_connectivity(metric_name, condata, self.pux.copy())
        #        avg = conn.sum() / len(conn)
        #        reached.append(conn.sum())
        #        avg_per_node.append(avg)
        #        print("\n", condata.name, "\nMetric: ", metric_name, "\nTotal:", metric.sum, "\nTarget:", metric.target, "\nTotal metric:", conn.sum(), "\nAvg per pu:", avg)
        #self.metrics_total = pd.DataFrame(list(zip(data_name, name, total, min_value, max_value, min_threshold, max_threshold, target, reached, avg_per_node)), columns = ['data', 'metric', 'total', 'min', 'max', 'min_threshold', 'max_threshold', 'target', 'total_metric', 'avg_per_pu'])
        #return self.metrics_total

    def total_cost(self, conservation):
        temp_pux = self.pux.merge(conservation.pu['cost'], left_on='pu', right_on=conservation.pu['id'], how='left')
        return temp_pux.loc[temp_pux['x'] == 1, 'cost'].sum()

    def analyze_post_connectivity(self, metric_name, connectivity):
        metric = connectivity.get_metric(metric_name)
        g = connectivity.g
        out_nodes = list(self.pux.loc[self.pux['x'] == 0]['pu'])
        g.remove_nodes_from(out_nodes)
        sol_metric = ConnectivityMetric(metric_name)
        sol_metric.g = g
        sol_metric.set_connectivity_metrics(sol_metric.g)

        return sol_metric.values['value']

    def analyze_connectivity(self, metric_name, condata, co_best):

        if metric_name == 'ec':
            metric = condata.get_metric(metric_name)
            #g = connectivity.g
            print(metric.metric_type)
            sol_metric = ConnectivityMetric(metric_name, metric.g)

            #sol_metric.g = connectivity["ec"].g
            sol_metric.set_connectivity_metrics()
            #sol_metric.set_connectivity_metrics(sol_metric.g)
            #print("cobest values")
            #print(co_best)
            co_best = co_best[co_best['x'] > 0]
            #print("cobest values > 1")
            #print(co_best)
            #print("solmet values")
            #print(sol_metric.values)
            cvalues = sol_metric.values.merge(co_best['x'], left_on='pu1', right_on=co_best['pu'])
            cvalues.rename(columns={'x': 'x1'}, inplace=True)
            #print("x1")
            #print(cvalues)
            cvalues = cvalues.merge(co_best['x'], left_on='pu2', right_on=co_best['pu'])
            cvalues.rename(columns={'x': 'x2'}, inplace=True)
            #print("x2")
            #print(cvalues)
            #cvalues = cvalues[cvalues['x1'] > 0]
            #cvalues = cvalues[cvalues['x2'] > 0]
            #print("only 1s")
            #print(cvalues)
            return cvalues['value']
        else:
            metric = condata.get_metric(metric_name)
            #g = connectivity.g
            sol_metric = ConnectivityMetric(metric_name, metric.g)
            #sol_metric.g = g
            #sol_metric.set_connectivity_metrics(sol_metric.g)
            sol_metric.set_connectivity_metrics()
            cvalues = sol_metric.values.merge(co_best['x'], left_on='pu', right_on=co_best['pu'])
            cvalues = cvalues[cvalues['x'] > 0]
            return cvalues['value']

    def show_map(self, path):
        # plot map
        #ax1 = self.pux.plot.scatter(x='xloc', y='yloc', c='x', colormap='viridis')
        #plt.savefig('output/conservation.pdf', bbox_inches='tight')

        sns.scatterplot(data=self.pux, x='xloc', y='yloc', hue='x')
        #plt.legend(labels = ['not selected', 'selected'], title='Conservation area', loc='upper right', frameon=False)
        #plt.legend(labels = ['not selected', 'selected'])
        legend = plt.legend()
        legend.get_texts()[0].set_text('not selected')
        legend.get_texts()[1].set_text('selected')
        #file.to_csv(os.path.join(path,name), index=False)
        name = 'solution_area.pdf'
        plt.savefig(os.path.join(path,name), bbox_inches='tight')
        plt.show()
