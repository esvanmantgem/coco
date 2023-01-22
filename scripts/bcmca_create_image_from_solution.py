import geopandas
import matplotlib.pyplot as plt
import pandas
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

shapefile = geopandas.read_file(
    'bcmca/BCMCA_ECO_Mammals_Chlorophyll_MARXAN.shp')

# cf
#solution = pandas.read_csv("../tests/BCMCA/grainscape_graph_as_connectivity_feature/solution.csv")
solution = pandas.read_csv("../tests/BCMCA/brandt/Pub/bcmca-con-ec/solution.csv")

#costcon
#solution = pandas.read_csv('../tests/BCMCA/optimizing_over_grainscape_graph/solution.csv')

merged_shp = shapefile.merge(solution, left_on='Unit_ID', right_on='pu', how='left')


merged_shp['geometry'] = merged_shp['geometry'].rotate(-35, origin=shapefile.unary_union.centroid)

cmap = ListedColormap(["lightskyblue", "yellow"])

ax = merged_shp.plot(column='x', cmap=cmap, missing_kwds={'color': 'lightblue'})

minx, miny, maxx, maxy = merged_shp.total_bounds
print(merged_shp.total_bounds)
#[ 341555.40408261   90263.76037868 1069422.9699731  1227097.30249512]
#This is the minimum for the reduced picture
minx = 650795.66148576
ax.set_xlim(685795.66148576, 999999.9599731)
ax.set_ylim(miny, 1117097.30149512)
#plt.axvspan(685795.66148576,999999.9599731 , facecolor='#207838', zorder=-100)
#plt.axvspan(minx,869422.7699731 , facecolor='lightblue', zorder=-100)
plt.axis('off')
plt.tight_layout()


#plt.savefig('output/solution_costcon.svg', format="svg", transparent='true',
#            bbox_inches='tight',
#            pad_inches=0.0)
#plt.savefig('output/solution_costcon.svg', format="pdf", transparent='true',
#            bbox_inches='tight',
#            pad_inches=0.0)

#plt.savefig('../tests/BCMCA/brandt/Pub/gap005-con-betcent-bestSpec-cost1166_nogap/solution.svg', format="svg", transparent='true',
#            bbox_inches='tight',
#            pad_inches=0.0)
plt.savefig('../tests/BCMCA/brandt/Pub/bcmca-con-ec/bcmca-con-ec.eps', format="eps", transparent='true',
            bbox_inches='tight',
            pad_inches=0.0)

plt.axis('off')
plt.show()
