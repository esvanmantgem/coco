# Marxan Connect Paper
## Abstract
1. Marxan requires manual input or specialized scripts to explicitly consider connectivity
2. Marxan Connect (MC) open source, open access GUI, relies on Marxan 2.4.3
3. Facilitates the use of demographic connectivity or structural landscape connectivity by calculating connectivity metrics and treat them as conservation feature or include it as spatial dependency amongst sites in prioritization
4. More likely to support persistent and resilient metapopulations

## Understanding Connectivity Data
* Connectivity data is mostly stored as a connectivity matrix or as an edge list
* For demographic data the strength of the connectivity is measured as a probability or absolute amount
* The strength of landscape connectivity is based on Euclidean distance or Isolation by resistance
      * The probability then is 1/distance^2 if pairs of pu's containt the same habitat type and are row normalized
* Larger values represent stronger connectivity

## Using Connectivity Data in Spatial Prioritization
* Different quantitative methods to incorporate connectivity data into Marxan workflow
    * Treat connectivity properties of pu's as conservations features for which a target is set (MC)
    * Include connectivity strengths among pu's as spatial dependencies within the objective function (MC)
    * Treat connectivity properties of pu's as connectivity cost (Bad)
    * Customize the objective function to incorporate connectivity performance metrics (Not done)
### Treat connectivity data as conservation feature
  * r_ik is amount of connectivity feature k in pu i
  * A representation target is set of each feature, Tk (e.g., 50%) as a threshold to be met
### Use directional connectivity data to inform the boundary cost (cv_ih)
  * This cost signifies the penalty associated with protecting site i but not other sites h to which it is strongly connected.
  * Because MC relies on Marxan, only one type of spatial dependency can be accepted
    * Users must choose between accounting for ecological connectivity of spatial congruence when defining spatial dependencies

## Marxan Connect
* MC is designed to help conservation practitioners incorporate connectivity data into Marxan analysis
* MC has a GUI that organizes the workflow into six steps:
    1. Spatial input: identify and load pu's and optionally avoidance or focus areas
    2. Connectivity input: demographic or landscape-based data (can rescale but better at resolution of pu's)
        * Landscape connectivity: MC calculates connectivity metrics based on Euclidean distance or least-cost paths between centroids of pu's. Alternatively Circuitscape, Conefor
    3. Connectivity metrics: select connectivity metric to use, calulates the metrics and establishes how to be treated (conservation feature or spatial dependencies)
    4. Pre-evaluations: discretize, edit and remove connectivity metrics. Set threshold(s) s.t. pu's meeting the threshold are marked as such (see Fig. 2). Also used with species distribution models, where each pu is assigned a probability of species occurence and a threshold value is used to discretize (binarize)
    5. Marxan files
    6. Marxan Analysis
    7. Plotting options

## Great Barrier Reef Case Study

