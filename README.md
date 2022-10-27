# Coco: Conservation Design for Optimal Ecological Connectivity

Coco provides an open source ILP solution for variations of the Reserve Selection problem including connectivity functionality.

Note: this is a pre-release version and not a full version yet

#### Install dependencies:

We recommend using a conda environment (https://conda.io) with Python version 3.10.6 and install the following packages:

* Geopandas 0.11.1:
```
conda install --channel conda-forge geopandas
```
* Gurobi 9.5.2: a Gurobi license is needed to run Coco (https://www.gurobi.com/). Inside the conda environment run:
```
python -m pip install gurobipy
```
* Seaborn 0.12.0:
```
conda install -c anaconda seaborn
```

#### Dependencies

* Python 3.10.6
* Geopandas 0.11.1
* Pandas 1.4.4
* Matplotlib 3.5.3
* NetworkX 2.8.6
* Seaborn 0.12.0
To run go to code directory:

#### How to run
```
cd src
```
To run Coco enter:
```
python main.py --help
```
This will show all available parameter settings
