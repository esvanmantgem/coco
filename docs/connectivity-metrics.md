## Marxan Connect Metrics
* MC can calculate various network metrics and ecologically meaningful measures
* see useful references at MC glossary

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

#### Eigenvector Centrality
* M
* indicates the influence (number of connections and their weight) a pu has on the network
* requires edge weights (quality)
* does not work well on a sparsely connected network
* prioritize pu's important to maintaining/influencing connectivity dynamics across the whole planning area

#### Google PageRank
* F, M, P
* indicates the importance of a pu based on number and quality (weight) of connections associated with pu
* functionally similar to Eigenvector Centrality
* recommended for well connected networks
* prioritize pu's important to maintaining/influencing connectivity dynamics across the whole planning area

#### Self-Reqruitement
* M
* indicates proportion of individuals arriving at pu that also originated from same pu
    * main diagonal of M
* prioritize pu's that are dominated by locally produced individuals
    * may indicate greater degree of isolation
    * caution: does not equate high reqruitment (100% self-reqruiting if only 1 individual arrives)
#### Local Retention
* P
* indicates proportion of individuals originating for a pu that are retained in that pu
    * main diagonal of P
    * value is independent of contributions from all other pu's
* prioritize pu's that retain a large proportion of the individuals produced
    * may indicate the ability of the pu to be self-sustaining

#### In-Flow / In-Flux
* F while ignoring main diagonal
* indicates number of incoming individuals without the individuals originating at the pu
* prioritize pu's receiving larger numbers of individuals from other pu's

#### Out-Flow / Out-Flux
* F while ignoring main diagonal
* indicates number of outgoing individuals without the individuals originating at the pu
* prioritize pu's that subsidize other pu's

#### Temporal Connectivity Covariance
* WARNING: experimental
* ignore for now

## New Connectivity Metrics
#### Metapopulation Capacity
