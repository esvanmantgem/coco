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

To run Coco enter:
```
python main.py -strategy <strategy_name> [strategy params]
```

### Coco RSP variants
Currently, Coco has three RSP variants installed:
* RSP with Connectivity Features (RSP-CF)
* RSP with Cost Connectivity (RSP-CC)
* RSP with Connectivity (RSP-Con).

```
-strategy {cf, cost-con, con}
```
Where `cf` is RSP-CF, `cost-con` is RSP-CC and `con` is RSP-Con

### Global parameter settings
The following parameters are available for all RSP variants:

#### I/O parameters
Here we explain the parameters in Coco for input and output files and folders. For more information on the input files needed and output files created, see the documentation in the  `doc` folder.

To specify the input folder:
```
-input INPUT_FOLDER
```
This can either be a relative or absolute path. This folder should contain all files needed for the basic RSP.

To specify the output folder:
```
-output OUTPUT_FOLDER
```
This can either be a relative or absolute path.

##### Connectivity data
The data to be used in the connectivity metric can be provided in different formats. For all formats either a relative path or an absolute path to the file can be given. For an explanation of the exact format of the files, see the documentation in the `doc` folder.

If only one connectivity dataset should be considered, one connectivity edgelist can be provided
```
--con-edgelist FILE
```
In case multiple connectivity dataset should be considered, e.g., one for each feature, one habitat-edgelist can be provided containing all datasets for each feature.
```
--habitat-edgelist FILE
```

Alternatively, one connectivity matrix can be specified
```
--con-matrix FILE
```

In case the selected metric, e.g., equivalent centrality, requires input data for each planning unit, this should be provided using:
```
--pu-data FILE
```
#### Metric parameters

We currently have the following metrics installed: indegree, outdegree, betweenness centrality and equivalent centrality. For more information on each metric, see the documentation in the `doc` folder. We are expanding the number of metrics Coco has installed, for requests feel free to contact me.

To specify the metric(s) used:
```
-metric {betcent, indegree, outdegree, ec}
```
Coco can run multiple metrics at the same time. To do this repeat the parameter for each metric you want to run, e.g., if we want to run betweenness centrality and equivalent centrality:
```
-metric betcent -metric ec
```

To exclude planning units with metric values under/above a specified threshold value from the connectivity optimization, set:
```
-metric-min VALUE
```
or
```
-metric-max VALUE
```

To exclude planning units with metric values under/above a value depending on the median or mean value of all metric values:
```
-metric-min-type {median, mean}
```
or
```
-metric-max-type {median, mean}
```
Note that the values below/above the selected type will be dropped for all metrics

### RSP-CF parameters
```
-metric-prop
```
```
-metric-target
```

### RSP-CC parameters
```
-metric-weight
```
```
-cost-weight
```

### RSP-Con parameters
```
-max-cost
```
```
-min-cost
```

