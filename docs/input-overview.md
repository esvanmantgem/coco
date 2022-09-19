# Input

## Marxan:

### Input files:

#### Conservation Features (spec.dat):
  * id: required
  * name: name of feature
  * target: target amount of feature to be in the solution (either target or prop required)
  * prop: minimum percentage of the feature to be covered in the solution
  - spf: feature penalty target
  - target2: minimal clump size required
  - targetocc: nr of pu's the feature needs to occur in

#### Planning Unit (pu.dat):
  * id: required
  * cost: cost of including pu in reserve system
  * xloc: x location of pu
  * yloc: y location of pu
  - status: defines if a pu is in or out of final reserve

#### Planning Unit vs Conservation Feature (puvspr.dat):
  * species: feature id
  * pu: pu id
  * amount: amount of feature in pu

#### Boundary Lenght File (bound.dat, not required):
  * id1: id of first pu
  * id2: id of second pu
  * amount: relative measure of importance to include id2 if id1 is included (boundary cost)

### Datastructure

#### Conservation Features (species):
  * id: required index
  * name: name of feature
  * target: target amount of feature to be in the solution (either target or prop required)
  * prop: minimum percentage of the feature to be covered in the solution


#### Planning Units (pu):
  * id: required index
  * cost: cost of including pu in reserve system
  * xloc: x location of pu
  * yloc: y location of pu

#### Planning Unit vs Conservation Feature (puvspr):
  * puvspr_id: required index
  * pu: pu id
  * species: feature id
  * amount: amount of feature in pu

#### Planning Unit Decision Variables (runtime):
  * pu: pu id
  * x: decision variable of pu_id

## Marxan Connect

### Connectivity Types

#### Demographic Connectivity
* Derived from animal tracking data, dispersal models, genetic tools, etc

#### Landscape Connectivity
* Spacial isolation, isolation by resistance, etc.
* Based on Euclidian distance, least cost path, isolation by resistance (Circuitscape, Conefor)
* Probability of connectivity is 1/distance^2 if pairs of pu's contain the same habitat type and are row normalized (sum of probabilities = 1)
* MC can calculate Euclidian distance and least cost path between centroids of pu's

### Connectivity Data Types
  * q: are these matrices per species or overall?

#### Flow Matrix
* data represents amount of movement between source (row) and destination (column)
* zero indicates no movement
* larger values represent greater flow
* if sum of received is smaller than sum produced (losses due to death or leaving), total produced should be provided
* can also be an edge list
  * q: where should Local Production (total produced) be provided?
  * q: is this the number of indiviuals?

#### Migration
* proportion of individuals at destination (column) pu relative to source (row) pu
* columns add up to 1 (100% of individuals in destination pu)
* adopted from see MC glossary
* can also be an edge list

#### Probability
* proportion of individuals originating from source (row) arriving at dest (column)
* interpretation: arrival likelyhood

### Connectivity File Datastructures
#### Connectivity Matrix
* sources are rows, destinations are columns
* first row and column contain source and destination pu ids
* should be NxN matrix with source ids == destination ids, in same order (for MC)
* cells contain info about connectivity from source to destination
  * value depends on the type of connectivity matrix (flow, migration, probability)
* need to implement

#### Edge List
* equivalent alternative to Connectivity Matrix
* first column (id1) contains source, second column (id2) contains destination, third column (value) contains value depending on type of connectivity matrix
* only non-zero values are represented by a row

#### Edge List with Habitat
* one egde list with habitat per each unique species
* first column contains habitat (habitat), second column (id1) contains source, third column (id2) contains destination, fourth column (value) contains value depending on type of connectivity matrix
* need to implement

#### Edge List with Time
* one edge list for each unique time-step
* first column contains time step id (time), second column (id1) contains source, third column (id2) contains destination, fourth column (value) contains value depending on type of connectivity matrix


#### Edge List with Type
* one edge list per species containing each unique species type id
* first column contains species id (type), second column (id1) contains source, third column (id2) contains destination, fourth column (value) contains value depending on type of connectivity matrix
* need to implement
