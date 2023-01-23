# Coco Connectivity Metrics

## Betweenness Centrality (BC)
The BC indicates the relative number of all shortest paths that pass through a vertex `v`. More formally, given a graph `G = (V,E)` the BC of a vertex `v` in `V` is given by:
```
BC(v) = (sp(s,t|v) / sp(s,t)) for all s,t pairs
```
The BC of `v` is the fraction of all shortest paths between vertices `s` and `t` that go through `v`. Ecologically, the BC prioritizes planning units that may act as stepping-stones between other planning units. As such, it is often used for long-range connectivity.

## Equivalent Connectivity
The EC is a metric that can be used for different purposes, depending on the type of attributes used. It maximizes the planning units with a high attribute value and a high closeness, i.e., inverse distance value. Given a link `e` between planning units `i` and `j`, the EC is given by:
```
EC(e) = a(i) a(j) d(ij)
```
Where `a(i)` is an attribute value of planning unit `i`, e.g., area size, habitat quality, and `d(ij)` is an inverse measure of functional or structural distance between `d(ij)`. Note, that for closely related planning units, the `d(ij)` should be high, e.g., in case of resistance values, this can be achieved by setting `d(ij) = 1/resistance value`.

## In-Degree
The indegree maximizes the sum of the indegree of the selected planning units. It selects planning units that have a high flow towards them and as such are important destination planning units.

## Out-Degree
The outdegree maximizes the sum of the outdegree of the selected planning units. It selects units that have many resources spreading to other planning units and may select planning units that have a high influenceo on other planning units.


