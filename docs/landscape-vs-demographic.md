## Question:
* Is there any difference in the processing when using landscape data instead of demographic data? 

## Landscape: 
* input: pu.dat, spec.dat, puvspr.dat, bound.dat
* connectivity input: 
    * either: habitat type shapefile -> contains info on bioregion. 
is used to calculate the isolation (or resistance but this is not fully functional) 
    * Uses either euclidian distance or ? 
    * or: edge list with habitat, contains habitat type 
      donor site ID (<- only probabilities), recipient site ID and connectivity value. 
    * Duplicate list for each unique type (species or dispersal trait)? 
    * Question: I don't see how to put multiple edge lists in MC? 
    * Question: Why is probability okay for landscape but flow and migration not?
    * Reminder: Probability connectivity value: amount of individuals arriving at 
     recipient unit.
* connectivity metrics available:

