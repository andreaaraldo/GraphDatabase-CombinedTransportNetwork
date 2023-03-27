# Pavage de la ville et creation des centroides
# Cree les fichiers 'distances.txt', 'pos_centroids.txt', 'pos_stations.txt'
import inspect
import pandas as pd
import matplotlib.pyplot as plt
import shapely
from shapely.geometry import Polygon, LineString, Point
import geographiclib
from geographiclib.geodesic import Geodesic
import geopandas as gpd
from shapely.geometry import Polygon
import numpy as np
import time

start_time = time.time()

geod = Geodesic.WGS84

# Importe 'stops.txt' & cree les points limites
stops = pd.read_csv(r'./Data/stops.txt') # stops = pd.read_csv(r'Data/stops.txt') for mac and linux
min_lat = min(stops.stop_lat) # Coordonnées limites des stops
max_lat = max(stops.stop_lat)
min_lon = min(stops.stop_lon)
max_lon = max(stops.stop_lon)
point_up_left = Point(min_lon, max_lat) # Points geometriques des limites
point_up_right = Point(max_lon, max_lat)
point_down_left = Point(min_lon, min_lat)
point_down_right = Point(max_lon, min_lat)

# Calcule la largeur et la longueur de la ville
larg = geod.Inverse(point_up_left.y, point_up_left.x, point_up_right.y, point_up_right.x)
largeur = larg['s12']/1000 # largeur en km
long = geod.Inverse(point_up_left.y, point_up_left.x, point_down_left.y, point_down_left.x)
longueur = long['s12']/1000 # Longueur en km
### Ville & contours
Ville = Polygon([point_up_left, point_up_right, point_down_right, point_down_left])
plt.scatter(stops.stop_lon, stops.stop_lat)
plt.plot(*Ville.exterior.xy)
plt.show()

# Cree pavage (polygones)
lon = (max_lon - min_lon)/int(np.floor(largeur))
lat = (max_lat - min_lat)/int(np.floor(longueur))
cols = int(np.floor(largeur))
rows = int(np.floor(longueur))
lat_down = min_lat
lon_right = max_lon
polygons = []
for i in range(cols):
   lat_up = max_lat
   lon_left = min_lon + lon*i
   for j in range(rows):
        polygons.append(Polygon([(lon_left, lat_up), (lon_left + lon, lat_up), (lon_left + lon, lat_up - lat), (lon_left, lat_up - lat)])) 
        lat_up = lat_up - lat
grid = gpd.GeoDataFrame({'geometry':polygons})
for i in range(len(polygons)):
    plt.plot(*polygons[i].exterior.xy)
plt.scatter(stops.stop_lon, stops.stop_lat)

## Centoids of polygons on Royan
plt.scatter(stops.stop_lon, stops.stop_lat)
plt.scatter([polygons[i].centroid.x for i in range(len(polygons))], [polygons[i].centroid.y for i in range(len(polygons))], marker = '.')
plt.show()

# Centroids
centroids0 = []
for i in range(len(polygons)):
    centroids0.append(Point(polygons[i].centroid.x, polygons[i].centroid.y))
        
centroids_coord = pd.DataFrame()
centroids_coord['centroid_id'] = [i for i in range(len(centroids0))]
centroids_coord['centroid'] = [i for i in centroids0]

centroids_pos = pd.DataFrame()
centroids_pos['centroid_id'] = centroids_coord.centroid_id
centroids_pos['longitude'] = [centroids0[i].x for i in range(len(centroids0))]
centroids_pos['latitude'] = [centroids0[i].y for i in range(len(centroids0))]
centroids_pos.to_csv(r'.\Data\pos_centroids.txt', index = False) # fichier 'pos_s=centroids.txt'

# Stops
stations0 = []
for i in range(len(stops)):
    stations0.append(Point(stops.stop_lon[i], stops.stop_lat[i]))

stations_coord = pd.DataFrame()
stations_coord['stop_id'] = stops.stop_id
stations_coord['station'] = [i for i in stations0]

stations_pos = pd.DataFrame()
stations_pos['stop_id'] = stations_coord.stop_id
stations_pos['longitude'] = [stations_coord.station[i].x for i in range(len(stations_coord))]
stations_pos['latitude'] = [stations_coord.station[i].y for i in range(len(stations_coord))]
stations_pos.to_csv(r'./Data/pos_stations.txt', index = False) # fichier 'pos_stations.txt'

# Distances Centroid-Stop
def dist(p1, p2): # fonction pour calculer la distance entre 2 points geometriques
    d = geod.Inverse(p1.y, p1.x, p2.y, p2.x)
    dist = d['s12']
    return dist

index_centroid = []
index_station = []
distance = []
for i in range(len(centroids_coord)):
    for j in range(len(stations_coord)):
        distance.append(round(dist(stations_coord['station'][j], centroids_coord['centroid'][i]),3))
        index_centroid.append(centroids_coord['centroid_id'][i])
        index_station.append(stations_coord['stop_id'][j])
index_station0 = [np.where(stations_coord['stop_id'] == index_station[i])[0][0] for i in range(len(index_station))]
tab = pd.DataFrame()
tab['centroid_id'] = [i for i in index_centroid]
tab['distance'] = distance
tab['stop_id'] = [i for i in index_station]

tab.to_csv(r'./Data/distances.txt', index = False) # Fichier 'distances.txt'

end_time = time.time()
print("temps d'exécution :", end_time - start_time)
print((end_time - start_time)/60, 'minutes')
