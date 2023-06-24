# Cree le fichier 'centroids.txt' regroupant les informations des futurs noeuds Centroid
# Nettoyage des centroides
import numpy as np
import pandas as pd
import Parameters
import time
import os
import Parameters

Data = Parameters.Data

start_time = time.time()

path_distances = os.path.normpath('./{}/distances.txt'.format(Data))
distances = pd.read_csv(path_distances)

path_pos_centroids = os.path.normpath('./{}/pos_centroids.txt'.format(Data))
pos_centroids = pd.read_csv(path_pos_centroids)

path_pos_stations = os.path.normpath('./{}/pos_stations.txt'.format(Data))
pos_stations = pd.read_csv(path_pos_stations)

rayon_exclusif = Parameters.rayon_exclusif
rayon_walk = Parameters.rayon_walk
departure_time = Parameters.departure_time
vitesse_walk = Parameters.vitesse_walk * 1000 / 3600

# Tri des centroides
df_dist_min = distances.groupby('centroid_id')['distance'].min().reset_index()
dist_reduced = df_dist_min[df_dist_min['distance'] <= rayon_exclusif]
id_centroid_reduced = dist_reduced['centroid_id'].tolist()

# Selection des relations WALK
dists_vf = []
index_centroid = []
index_station = []
longitudes = []
latitudes = []
for i in id_centroid_reduced:
    dists = distances.distance.iloc[np.where(distances.centroid_id == i)].values
    stations = distances.stop_id.iloc[np.where(distances.centroid_id == i)].values
    idx_walks = np.where(dists <= rayon_walk)[0]
    if len(idx_walks) != 0:
        walk_dists = [dists[k] for k in idx_walks]
        idx_walks = [np.where(dists == k)[0][0] for k in walk_dists]
        stations_walks = [stations[k] for k in idx_walks]
        for j in stations_walks:
            index_centroid.append(i)
            longitudes.append(pos_centroids.iloc[np.where(pos_centroids.centroid_id == i)].longitude.iloc[0])
            latitudes.append(pos_centroids.iloc[np.where(pos_centroids.centroid_id == i)].latitude.iloc[0])
            index_station.append(j)
            dists_vf.append(distances.iloc[np.where((distances.centroid_id == i) & (distances.stop_id == j))].distance.iloc[0])
    else:
        idx_1000 = np.where(dists <= 6500)[0]
        min_dist = np.min([dists[i] for i in idx_1000])
        idx_min = np.where(dists == min_dist)[0]
        station_min = stations[idx_min][0]
        index_centroid.append(i)
        longitudes.append(pos_centroids.iloc[np.where(pos_centroids.centroid_id == i)].longitude.iloc[0])
        latitudes.append(pos_centroids.iloc[np.where(pos_centroids.centroid_id == i)].latitude.iloc[0])
        index_station.append(station_min)
        dists_vf.append(distances.iloc[np.where((distances.centroid_id == i) & (distances.stop_id == station_min))].distance.iloc[0])

centr = pd.DataFrame()
centr['centroid_id'] = index_centroid 
centr['longitude'] = longitudes
centr['latitude'] = latitudes
centr['distance'] = dists_vf 
centr['stop_id'] = index_station

centroid_vf = pd.DataFrame()
centroid_vf['centroid_id'] = centr['centroid_id']
centroid_vf['centroid_lon'] = centr['longitude']
centroid_vf['centroid_lat'] = centr['latitude']
centroid_vf['distance'] = round(centr['distance'],3)
centroid_vf['stop_id'] = centr['stop_id']
centroid_vf['departure_time'] = [departure_time]*len(centroid_vf)
centroid_vf['walking_time'] = round(centroid_vf['distance']/vitesse_walk,3)

path_centroids = os.path.normpath('./{}/centroids.txt'.format(Data))
centroid_vf.to_csv(path_centroids, index = False) # Fichier 'centroids.txt'

end_time = time.time()
print("temps d'exécution :", end_time - start_time)
print((end_time - start_time)/60, 'minutes')