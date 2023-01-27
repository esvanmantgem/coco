# Input files
We require input files very similar to Marxan. The name of each file should be as specified in this document. The heading of each file, i.e., the name of each column, should be exactly as specified.

For an example of each file type, see the `example_files` folder.

Each file description begins with a description of the data follows by the filename and file extension. Then a list follows where each item in the list specifies the column name and a description of the values, possible properties and an indication if this column is required. The structure of each file description is as follows:

#### Name of the data (`<filename>.<extension`):
Short description of the data.
File format specification:
  * `<column_name1>`: `<description of the values>`
  * `<column_name2>`: `<description of the values>`

All `cvs` files should be comma separated. This means the a filled called `<filename>.csv` has the following structure:
```
column_name1, column_name2
v1, v2
v3, v4
...
vx, vy
```

#### Conservation Features (`feature.csv`):
Contains the features to be considered for conservation. Each feature has a unique id and the target to be reached, either set as a proportion or the target value directly. Either target or prop is required.
  * `feature`: a unique integer, functioning as identifier for each feature (required)
      - in this document we refer to this id as feature id
  * `target`: target amount of the feature to be in the solution
  * `prop`: minimum percentage of the feature to be covered in the solution
  * `name`: name of feature (optional)

Note that other files, e.g., `feature-edgelist.csv`, also use feature ids. Not all used features require to have a target set and so not all features have to be listed in the `feature.csv`. Only list those features for which a target needs to be reached in the conservation area.
The `feature.csv` is required and should be located in the input folder

#### Planning Unit (`pu.csv`):
Contains the planning units of the planning area considered for conservation. Each planning unit has a unique id and a cost (the cost should be higher than 0).
  * `pu`: a unique integer, functioning as identifier for each planning unit (required)
      - in this document we refer to this id as pu id
  * `cost`: cost of each planning unit in the planning area (required)
  * `xloc`: x location of pu (optional)
  * `yloc`: y location of pu (optional)

The `pu.csv` is required and should be located in the input folder

#### Planning Unit vs Conservation Feature (`pvf.csv`):
Contains the occurrence, `value`, of each feature in each planning unit. If a feature is not present in a planning unit, i.e., the value of amount would be 0, this record should not be in the list.
  * `feature`: feature id (required)
  * `pu`: pu id (required)
  * `value`: amount of the feature in the planning unit (required)

The `pvf.csv` is required and should be located in the input folder


### Connectivity Data
Connectivity data is needed for the connectivity metrics. Coco accepts connectivity data in matrix or edgelist format. The information contained in both formats are the same, the only difference is that they are stored in another datastructure. Note that a matrix and a basic edgelist can only contain data for one feature, while a habitat edgelist can contain data for multiple features. We advice to use a habitat edgelist in case connectivity data is supplied per feature.

#### Edgelist (`<file_name>`.csv):
The edgelist contains data from source (`pu1`) to destination (`pu2`). Meaning that the values per row indicate the connectivity value from planning unit `pu1` to planning unit `pu2`. Note that rows containing zero values should not be in the edgelist and should be removed before use.
  * `pu1`: pu id of the source planning unit (required)
  * `pu2`: pu id of the destination planning unit (required)
  * `value`: value to be used in the metrics on the link between planning unit `pu1` and planning unit `pu2`

#### Edge List with Habitat ('<file_name>'.csv):
The edgelist with habitat is similar to the edgelist. The only distinction is that the file can contain connectivity data for different features.
  * `feature`: feature id indicating the feature the value relates to. The feature id should be the same as in the `feature.csv` in case both refer to the same feature. If it contains data about a new feature, make sure the feature id is not in use yet, e.g., not in the `feature.csv` (required)
  * `pu1`: pu id of the source planning unit (required)
  * `pu2`: pu id of the destination planning unit (required)
  * `value`: value to be used in the metrics on the link between planning unit `pu1` and planning unit `pu2` considering feature `feature`

#### Connectivity Matrix (`<file_name>`.csv):
The connectivity matrix is an equivalent alternative to the edgelist with a different datastructure. In the connectivity matrix we have one row per source and one column per destination. Each cell contains information about the connectivity from source to destination. Thus the value in row `i` and column `j` contains data on the link going from planning unit `i` to planning unit `j`.

The first row of the matrix contains the pu id's of each planning unit to be considered. This order is assumed to be the same for each row.

#### Planning unit attribute data (`<file_name>.csv`):
This optional `csv` file contains attribute data of planning units in case this is required by metrics. Currently, this is only needed for the equivalent connectivity (EC), which needs attribute data per feature per planning unit
  * `feature`: feature id, this feature id should be the same as the feature id used in the edgelist (required)
  * `pu`: pu id (required)
  * `value`: the values of the attribute for the feature in the planning unit (required)

