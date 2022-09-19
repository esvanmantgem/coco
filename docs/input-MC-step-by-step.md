## Step by step input explanation

1. Shapefile (e.g. hex_planning_unit.sh) -> Contains the following columns:  
    1. **ID**
    2. **Geometry** (Provides coordinates for each POLYGON(in our case a hexagon), which is a Shapely-object. Each Polygon looks as follows: POLYGON((x y, x y, x y, x y, x y, x y)) -> double parethesis because a polygon-object can have holes(ours don't)), 
    3. **BIORE_x** <- several columns of Bioregions. Value is NaN if the planning unit is not part of the bioregion (i think)
2. 