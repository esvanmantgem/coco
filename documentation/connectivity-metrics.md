# Coco Connectivity Metrics

#### In-Degree
* F, M, P
* indicates in-degree of each pu
* ignores edge weights
* prioritize pu's receiving input from larger number of pu's
  * may have higher genetic diversity, species diversity and population resilience
  * may be susceptible to outbreaks and invasive species

#### Out-Degree
* F, M, P
* indicates out-degree of each pu
* ignores edge weights
* prioritize pu's with higher number of outgoing edges
  * may have larger influence on other pu's
  * pu's with extremely high out-degree are considered hubs, may influence local and network-wide dynamics

#### Betweenness Centrality
* F, M, P
* indicates the relative number of all shortest paths that pass through focal pu
* ignores edge weights
* prioritize pu's that may act as stepping stones among other pu's

