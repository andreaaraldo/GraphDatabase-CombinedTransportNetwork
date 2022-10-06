# Pavage de la ville : encadrement de la ville puis quadrillage
# Récupère les centroïdes des pavés de 1km²
# Crée les fichiers : centroids.txt pour la création des noeuds Centroid, distances.txt pour sauvegarder les distances entre chaque centroïde et station
import inspect
import pandas as pd
import matplotlib.pyplot as plt
import shapely
from shapely.geometry import Polygon, LineString, Point
import geographiclib
from geographiclib.geodesic import Geodesic


# Load 'stops.txt' & create points
stops = pd.read_csv(r'.\Data\stops.txt')

min_lat = min(stops.stop_lat)
max_lat = max(stops.stop_lat)
min_lon = min(stops.stop_lon)
max_lon = max(stops.stop_lon)

point_up_left = Point(min_lon, max_lat)
point_up_right = Point(max_lon, max_lat)
point_down_left = Point(min_lon, min_lat)
point_down_right = Point(max_lon, min_lat)


# Calculate width & height in meters
geod = Geodesic.WGS84

larg = geod.Inverse(point_up_left.y, point_up_left.x, point_up_right.y, point_up_right.x)
largeur = larg['s12']/1000 # largeur en km

long = geod.Inverse(point_up_left.y, point_up_left.x, point_down_left.y, point_down_left.x)
longueur = long['s12']/1000 # Longueur en km


### Ville & contours
Ville = Polygon([point_up_left, point_up_right, point_down_right, point_down_left])
plt.scatter(stops.stop_lon, stops.stop_lat)
plt.plot(*Ville.exterior.xy)


# Create grid (polygons)
import geopandas as gpd
from shapely.geometry import Polygon
import numpy as np


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


# Distances : centroids-stations
### Centroids
centroids0 = []
for i in range(len(polygons)):
    centroids0.append(Point(polygons[i].centroid.x, polygons[i].centroid.y))
        
centroids = pd.DataFrame()
centroids['centroid_id'] = [i for i in range(len(centroids0))]
centroids['centroid'] = [i for i in centroids0]
centroids

positions = pd.DataFrame()
centroids['centroid_id'] = centroids.centroid_id
centroids['longitude'] = [centroids0[i].x for i in range(len(centroids0))
centroids['latitude'] = [centroids0[i].y for i in range(len(centroids0))]


### Stations
stations0 = []
for i in range(len(stops)):
    stations0.append(Point(stops.stop_lon[i], stops.stop_lat[i]))
    
stations = pd.DataFrame()
stations['stop_id'] = stops.stop_id
stations['station'] = [i for i in stations0]
stations

df_pos = pd.DataFrame()
df_pos['stop_id'] = stations.stop_id
df_pos['lon'] = [stations.station[i].x for i in range(len(stations))]
df_pos['lat'] = [stations.station[i].y for i in range(len(stations))]
df_pos


# Distances
geod = Geodesic.WGS84

def dist(p1, p2):
    d = geod.Inverse(p1.y, p1.x, p2.y, p2.x)
    dist = d['s12']
    return dist

## Garde les distances stations <= 1 km ou la station la plus proche si il n'y en a pas dans le rayon de 1 km
rayon = 1000 # choix du rayon
dists_v2 = []
index_centroid = []
index_station = []
for i in range(len(centroids)):
    dists_i = []
    for j in range(len(stations)):
        distance = dist(stations['station'][j], centroids['centroid'][i])
        if distance <= rayon:
            dists_v2.append(distance)
            index_centroid.append(centroids['centroid_id'][i])
            index_station.append(stations['stop_id'][j])
        else:
            dists_i.append(distance)
    if len(dists_i) == len(stations):
        dists_v2.append(min(dists_i))
        index_centroid.append(centroids['centroid_id'][i])
        index_station.append(stations['stop_id'][np.argmin(dists_i)])

index_station0 = [np.where(stations['stop_id'] == index_station[i])[0][0] for i in range(len(index_station))]

tab = pd.DataFrame()
tab['centroid_id'] = [i for i in index_centroid]
tab['centroid'] = [centroids['centroid'][i] for i in index_centroid]
tab['distances'] = dists_v2
tab['stop'] = [stations['station'][i] for i in index_station0]
tab['stop_id'] = [i for i in index_station]
tab

centroid_vf = pd.DataFrame()
centroid_vf['centroid_id'] = tab['centroid_id']
centroid_vf['centroid_lon'] = [tab['centroid'][i].x for i in range(len(tab))]
centroid_vf['centroid_lat'] = [tab['centroid'][i].y for i in range(len(tab))]
centroid_vf['distance'] = round(tab['distances'],3)
centroid_vf['stop_id'] = tab['stop_id']
centroid_vf['departure_time'] = ['\'08:30:00\'']*len(centroid_vf)
centroid_vf['walking_time'] = round(centroid_vf['distance']/0.83333,3)
centroid_vf
centroid_vf.to_csv(r'.\Data\centroids.txt', index = False) # Fichier 'centroids.txt'


# Distances centroid-stations (all)
index_centroid = []
index_station = []
distance = []
for i in range(len(centroids)):
    for j in range(len(stations)):
        distance.append(round(dist(stations['station'][j], centroids['centroid'][i]),3))
        index_centroid.append(centroids['centroid_id'][i])
        index_station.append(stations['stop_id'][j])

index_station0 = [np.where(stations['stop_id'] == index_station[i])[0][0] for i in range(len(index_station))]
tab = pd.DataFrame()
tab['centroid_id'] = [i for i in index_centroid]
tab['distances'] = distance
tab['stop_id'] = [i for i in index_station]

tab.to_csv(r'.\Data\distances.txt', index = False) # Fichier 'distances.txt'


