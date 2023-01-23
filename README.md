# Coco: Conservation Design for Optimal Ecological Connectivity

Coco provides an open source ILP solution for variations of the Reserve Selection problem including connectivity functionality.

Note: this is a pre-release version and not a full version yet

### Install dependencies:

We recommend using a conda environment (https://conda.io) with Python version 3.10.6 and install the following packages:

* Geopandas 0.11.1:
```
conda install --channel conda-forge geopandas
```
* Gurobi 9.5.2: a Gurobi license is needed to run Coco (https://www.gurobi.com/). Inside the conda environment run:
```
python -m pip install gurobipy
```

### Dependencies

* Python 3.10.6
* Geopandas 0.11.1
* Pandas 1.4.4
* Matplotlib 3.5.3
* NetworkX 2.8.6
* Seaborn 0.12.0
To run go to code directory:

### How to run
```
cd src
```
To run Coco enter:
```
python main.py -strategy <strategy_name> [strategy params]
```
The parameter `-strategy` sets the RSP variant Coco runs. Currently, Coco has three RSP variants installed: RSP with Connectivity Features (RSP-CF), RSP with Cost Connectivity (RSP-CC) and RSP with Connectivity (RSP-Con).

#### Global parameter settings
The following parameters are available for all RSP variants.
-input
-output
-strategy
-metric
-metric-min
-metric-min-type
-metric-max
-metric-max-type
--con-matrix
--con-edgelist
--habitat-edgelist
--pu-data


CF:
-metric-prop
-metric-target

CC:
-metric-weight
-cost-weight

CON:
-max-cost
-min-cost

