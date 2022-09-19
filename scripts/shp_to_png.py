import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

#zipfile = "../data/Germany_shapefile.zip"
file = 'hex_planning_units.shp'
shape = gpd.read_file(file)
#geo = shape['geometry']
# recreate geodataframe

# expand the co-ordinates
#print(geo.head(5))

pd.set_option('display.max_columns', 22)
print(shape)
shape.to_csv('shape_out.csv', index=False)
#plt.show()
#pu = pd.read_csv('input/pu.dat')
#ax1 = pu.plot.scatter(x='xloc', y='yloc', c='DarkBlue')
#shape.plot();
#plt.show()
