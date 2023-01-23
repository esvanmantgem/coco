# Input files
We require input files very similar to Marxan. The name of each file should be as specified in this document. The heading of each file, i.e., the name of each column, should be exactly as specified.

Each file description begins with a description of the data follows by the filename and file extention. Then a list follows where each item in the list specifies the column name and a description of the values, possible properties and an indication if this column is required. The structure of each file description is as follows:

#### Name of the data (`<filename>`):
Short description of the data.
File format specification:
  * `<column_name1>`: `<description of the values>`
  * `<column_name2>`: `<description of the values>`

#### Conservation Features (`spec.dat`):
Contains the features to be considered for conservation. Each feature has a unique id and the target to be reached, either set as a proportion or the target value directly. Either target or prop is required.
  * `id`: a unique integer, functioning as identifier for each feature (required)
      - in this document we refer to this id as feature id
  * `target`: target amount of the feature to be in the solution
  * `prop`: minimum percentage of the feature to be covered in the solution
  * `name`: name of feature (optional)

The `spec.dat` is required and should be located in the input folder

#### Planning Unit (`pu.dat`):
Contains the planning units of the planning area considered for conservation. Each planning unit has a unique id and a cost (the cost should be higher than 0).
  * `id`: a unique integer, functioning as identifier for each planning unit (required)
      - in this document we refer to this id as pu id
  * `cost`: cost of each planning unit in the planning area (required)
  * `xloc`: x location of pu (optional)
  * `yloc`: y location of pu (optional)

The `pu.dat` is required and should be located in the input folder

#### Planning Unit vs Conservation Feature (`puvspr.dat`):
Contains the occurrence, amount, of each feature in each planning unit. If a feature is not present in a planning unit, i.e., the value of amount would be 0, this record should not be in the list.
  * `species`: feature id (required)
  * `pu`: pu id (required)
  * `amount`: amount of the feature in the planning unit (required)

The `puvspr.dat` is required and should be located in the input folder

#### Planning unit attribute data (`<file_name>.csv`):
This optional `csv` file contains attribute data of planning units in case this is required by metrics. Currently, this is only needed for the equivalent centrality, which needs attribute data per feature per planning unit
  * `habitat`: feature id (required)
  * `pu`: pu id (required)
  * `amount`: the values of the attribute for the feature in the planning unit (required)

### Connectivity Data
Connectivity data is needed for the connectivity metrics. Coco accepts connectivity data in matrix or edgelist format. The information contained in both formats are the same, the only difference is that they are stored in another datastructure. Note that a matrix and a basic edgelist can only contain data for one feature, while a habitat edgelist can contain data for multiple features. We advice to use a habitat edgelist in case connectivity data is supplied per feature.

#### Edgelist (`<file_name`.csv):
The edgelist contains data from source (`pu1`) to destination (`pu2`). Meaning that the values per row indicate the connectivity value from planning unit `pu1` to planning unit `pu2`. Note that rows containing zero values should not be in the edgelist and should be removed before use.
  * `pu1`: pu id of the source planning unit (required)
  * `pu2`: pu id of the destination planning unit (required)
  * `value`: value to be used in the metrics on the link between planning unit `pu1` and planning unit `pu2`

#### Edge List with Habitat ('<file_name'.csv):
The edgelist with habitat is similar to the edgelist. The only distinction is that the file can contain connectivity data for different features.
  * `habitat`: feature id indicating the feature the value relates to (required)
  * `pu1`: pu id of the source planning unit (required)
  * `pu2`: pu id of the destination planning unit (required)
  * `value`: value to be used in the metrics on the link between planning unit `pu1` and planning unit `pu2` considering feature `habitat`

#### Connectivity Matrix (`<file_name`.csv):
The connectivity matrix is an equivalent alternative to the edgelist with a different datastructure. In the connectivity matrix we have one row per source and one column per destination. Each cell contains information about the connectivity from source to destination. Thus the value in row `i` and column `j` contains data on the link going from planning unit `i` to planning unit `j`.

The first row of the matrix contains the pu id's of each planning unit to be considered. This order is assumed to be the same for each row.

