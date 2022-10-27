import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import transforms
from shapely.geometry import Point
from geopandas.tools import sjoin

reefs = 'input/reefs.shp'
bios = 'input/bioregion_short.shp'
hexpus = 'input/hex_planning_units.shp'
back = gpd.read_file(bios)

reef = True
mc = False

#### COCO file
sol = pd.read_csv('../tests/mfp/con-strat/solution.csv')
#sol = pd.read_csv('../tests/hexflow/cost_only/solution.csv')
#sol = pd.read_csv('../src/output/solution.csv')
#sol = pd.read_csv('input/solution.csv')

##### MC Only
if mc:
    sol = pd.read_csv('../data/mc_mfp_res/output/connect_best.txt')
    pu = pd.read_csv('input/pu.dat')
    sol = sol.merge(pu, left_on='planning_unit', right_on='id', how='left')
    sol = sol.rename(columns={'planning_unit': 'pu'})
    sol = sol.rename(columns={'solution': 'x'})

####### Both

if reef:
    # real reef data
    geo = gpd.read_file(reefs)
    sol = sol[sol.pu != 262]
    sol = sol[sol.pu != 317]
    geoneo = geo.merge(sol, left_on='pu_id', right_on='pu', how='left')
    geometry = []
    for x,y,val in zip(sol['xloc'], sol['yloc'], sol['x']):
        geometry.append(Point(x,y))
    gdf = gpd.GeoDataFrame(sol, crs="EPSG:4326", geometry=geometry)
    #gdf.plot()

    both = gdf.sjoin(back, how="right", predicate='within')
    both['geometry'] = both.rotate(-23, origin=back.unary_union.centroid)

    ax = both.plot(column='x', cmap='cividis', missing_kwds={'color': 'lightblue'})
    plt.xlim([146.4,147.9])
    plt.ylim([-18.5, -12.6])
    plt.axvspan(146,147.2 , facecolor='#207838', zorder=-100)
    plt.axvspan(147.2,150, facecolor='lightblue', zorder=-100)
    plt.tight_layout()
    plt.axis('off')
    plt.savefig('output/solution.pdf',format="pdf", transparent='true', bbox_inches='tight',pad_inches=0.0 )
    plt.savefig('output/solution.png',format="png", transparent='true', bbox_inches='tight',pad_inches=0.0 )
    plt.savefig('output/solution.svg',format="svg", transparent='true', bbox_inches='tight',pad_inches=0.0 )
else:
    # hexflow synthetic
    geo = gpd.read_file(hexpus)
    geoneo = geo.merge(sol, left_on='FID', right_on='pu', how='left')
    geoneo['geometry'] = geoneo.rotate(-29, origin=back.unary_union.centroid)
    ax = geoneo.plot(column='x', cmap='cividis', missing_kwds={'color': 'lightblue'})
    plt.ylim([-9.994e+06, -9.017e+06])
    plt.tight_layout()
    plt.axis('off')

    plt.savefig('output/solution.svg',format="svg", transparent='true', bbox_inches='tight',pad_inches=0.0 )

plt.show()

###################### ignore this #################################




#144 - 148, -13 -19
#ui.plot()
#print(shape)
#geo = shape['geometry']
# recreate geodataframe

# expand the co-ordinates

#geo['geometry'] = geo.rotate(8, origin=geo.unary_union.centroid)
#back['geometry'] = back.rotate(8, origin=back.unary_union.centroid)


#print(back.head(4))
#temp_pux = self.pux.merge(conservation.pu['cost'], left_on='pu', right_on=conservation.pu['id'], how='left')
#for bc in back['geometry']:
    #print(bc)
    #print(bc.type)
#print("\n")
#print(back['geometry'])
#polys  = shape["geometry"]
#print(polys)
#poly = polys.iterShapes().next().__geo_interface__
#pd.set_option('display.max_columns', 22)
#shape.to_csv('shape_out.csv', index=False)
#plt.show()
#ax1 = pu.plot.scatter(x='xloc', y='yloc', c='DarkBlue')
#shape.plot();
#plt.show()

#BLUE = '#6699cc'
#fig = plt.figure()
#ax = fig.gca()
#ax.add_patch(PolygonPatch(poly, fc=BLUE, ec=BLUE, alpha=0.5, zorder=2 ))
#ax.axis('scaled')
#plt.show()
#geo.plot()
#x=geoneo.plot(column='x', cmap='cividis')
#back.plot(ax=x)

#ax1=geo_df1.plot()
#geo_df2.plot(ax=ax1)

#for pu in geoneo.values:
#    print(pu)
#pointInPolys = sjoin(geoneo, back, how='left')
#pointInPolys = sjoin(back, gdf, how='left')
#print(pointInPolys.head(5))
#back.crs
#print("back:", back.crs)
#print("geo:", geoneo.crs)
#geoneo.plot(column='x', cmap='cividis')
#back.plot()

#pointInPolys.plot(column='x', cmap='cividis')
#geoneo.to_crs(4326)
#test = gdf.geometry.clip(back)
#print(test)
#geoneo = geo.merge(sol)
#geo.assign(C=sol['x'])
#print(geoneo.head(5))
#polys  = shape.Reader("polygon")
# first polygon

#values = []
