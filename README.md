# Coco: Conservation Design for Optimal Ecological Connectivity

Coco provides and open source ILP solution for variations of the Reserve Selection problem including connectivity functionality

Note: this is a pre-release version and not a full version yet


#### Dependencies
* Python 3.10.6
* Geopandas 0.11.1
* Pandas 1.4.4
* Matplotlib 3.5.3
* NetworkX 2.8.6
* Seaborn 0.12.0

#### Installs
* Geopandas:
conda install --channel conda-forge geopandas
* Gurobi (inside conda env):
python -m pip install gurobipy
* Seaborn
conda install -c anaconda seaborn

To run go to code directory:
```
cd src
```
To run Coco enter:
```
python main.py --help
```
This will show all available parameter settings
