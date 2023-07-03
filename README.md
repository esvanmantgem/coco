# Coco: Conservation Design for Optimal Ecological Connectivity

Coco provides an open source ILP solution for variations of the Reserve Selection problem including connectivity functionality.

Note: this is a pre-release version and not a full version yet

## Installation:

We recommend using a conda environment (https://conda.io) with Python version 3.10.6 and install the following packages:

* Gurobi 9.5.2: a Gurobi license is needed to run Coco (https://www.gurobi.com/). Inside the conda environment run:
```
python -m pip install gurobipy
```
* Seaborn 0.12.0:
```
conda install -c anaconda seaborn
```

### Coco dependencies

* Python 3.10.6
* Pandas 1.4.4
* Matplotlib 3.5.3
* NetworkX 2.8.6
* Seaborn 0.12.0

#### Script dependencies

To run the scripts in the scripts folder, geopandas is needed. These scripts work only on the data provided in this repository.
* Geopandas 0.11.1:

```
conda install --channel conda-forge geopandas
```

## Running Coco

Go to the `src` folder:
```
cd src
```

### Coco RSP variants
Currently, Coco has three RSP variants installed:
* RSP with Connectivity Features (RSP-CF)
* RSP with Cost Connectivity (RSP-CC)
* RSP with Fixed Cost Connectivity (RSP-FCC).

To get help on how to run a specific variant, type:
```
python coco.py --help
```

To get help with the parameters of a specific variant `RSP-VARIANT`, type:
```
python coco.py RSP-VARIANT --help
```

To run Coco enter:
```
python coco.py RSP-VARIANT [global params] [variant params] [gurobi params]
```
Below we give a detailed explanation of each parameter

### Global parameter settings
The following parameters are available for all RSP variants:

#### I/O parameters
Here we explain the parameters in Coco for input and output files and folders. For more information on the input files needed and output files created, see the documentation in the  `doc` folder.

To specify the input folder (required):
```
--input INPUT_FOLDER
```
This can either be a relative or absolute path. This folder should contain all files needed for the basic RSP.

To specify the output folder (required):
```
--output OUTPUT_FOLDER
```
This can either be a relative or absolute path.

##### Connectivity data
The data to be used in the connectivity metric can be provided in different formats. For all formats either a relative path or an absolute path to the file can be given. For an explanation of the exact format of the files, see the documentation in the `doc` folder.

At least one of `--con-edgelist`, `feature-edgelist`, or `con-matrix` is required.
If only one connectivity dataset should be considered, one connectivity edgelist can be provided
```
--con-edgelist FILE
```
In case multiple connectivity dataset should be considered, e.g., one for each feature, one feature-edgelist can be provided containing all datasets for each feature. Note that the features in the edgelist do not have to be the same as in the `feature.csv`
```
--feature-edgelist FILE
```

Alternatively, one connectivity matrix can be specified
```
--con-matrix FILE
```

In case the selected metric, e.g., equivalent connectivity, requires attribute data for each planning unit, this should be provided using (optional):
```
--pu-data FILE
```
#### Metric parameters

We currently have the following metrics installed: indegree, outdegree, betweenness centrality and equivalent connectivity. For more information on each metric, see the documentation in the `doc` folder. We are expanding the number of metrics Coco has installed, for requests feel free to contact me.

To specify the metric(s) used (required):
```
--metric {bc, indegree, outdegree, ec}
```
Coco can run multiple metrics at the same time. To do this repeat the parameter for each metric you want to run, e.g., if we want to run betweenness centrality and equivalent connectivity:
```
--metric bc -metric ec
```

To exclude planning units with metric values under/above a specified threshold value from the connectivity optimization, set (optional):
```
--metric-min VALUE
```
or
```
--metric-max VALUE
```

To exclude planning units with metric values under/above a value depending on the median or mean value of all metric values (optional):
```
--metric-min-type {median, mean}
```
or
```
--metric-max-type {median, mean}
```
Note that the values below/above the selected type will be dropped for all metrics

If BC is the metric and the connectivity data is a complete graph, connectivity values from the input data below the `mean` or `median` can be dropped as follows:
```
--complete-graph {median, mean}
```
This is needed for BC, since by definition the BC for vertices in a complete graph is 0.

### RSP-CF parameters
The following parameters are only available for the RSP-CF variant. It is required to set exactly one of the following:

Set the target for the connectivity feature to be reached to a proportion of the total metric value:
```
--metric-prop VALUE
```
Set the target of the connectivity featerure to be reached to a specific value:
```
--metric-target VALUE
```
Note that these settings are applied to all considered metrics. In case of multiple metrics, `metric-prop` should be used since each metric can have very different values.

### RSP-CC parameters
The following parameters are only available for the RSP-CC variant. Both parameters are used to balance the weight between the cost and the metric values while optimizing.

To set the weight of the metric values (required):
```
--metric-weight
```

To set the weight of the cost (optional):
```
--cost-weight
```
Balancing this correctly requires some knowledge on the data and metric values. During optimization the metric values are min max normalized and thus can have values [0,1] on each vertex or edge depening on the metric. Setting the cost too low compared to the metric values will result in a negative objective value, which should be prevented at all times. Setting the metric values too low (especially in case of very small values) result in a longer runtime to find the optimal result.

### RSP-FCC parameters
The following parameters are only available for the RSP-FCC variant. It is required to set either one of the values. If a fixed cost is wanted, setting `-max-cost` is sufficient, since the optimizer will automatically maximize the connectivity values by taking as many planning units as possible, i.e., maximize the cost.

To set the max cost use:
```
--max-cost COST
```

To set the min cost use:
```
--min-cost COST
```

#### Gurobi related parameter settings
These settings are related to the ILP solver, Gurobi. In specific circumstances it might be helpful to adjust the standard settings of Gurobi. All these parameters are optional. For more information on these parameters visit the Gurobi documentation.

To set the minimal gap to the optimal solution that the solver has to find set:
```
--gap VALUE
```
The solver will stop when it find a solution within VALUE * 100% of the optimal value. It is not untypical for the ILP solver to find a solution close to optimal relatively quickly and then needing a lot of time to find the last percentages. In these cases, setting a gap will decrease the runtime significantly, without too much influence on the found solution (depending on the gap set).

Instead of setting a gap it is also possible to specify a time limit for the solver. This can be done by giving the max time in seconds after which the solver will report the best solution found:
```
--time-limit VALUE
```
Keep in mind that the total runtime of Coco will be longer than the time limit set since this only applies to time spent in the solver.

To set the number of threads used by Gurobi:
```
--gurobi-threads
```
To set the memory used by Gurobi:
```
--gurobi-mem
```
