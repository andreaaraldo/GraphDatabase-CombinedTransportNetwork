# # Cree le fichier 'centroids.txt' regroupant les informations des futurs noeuds Centroid
# # Nettoyage des centroides
# import numpy as np
# import pandas as pd
# import Parameters
# import time
# import os

# start_time = time.time()

# path_distances = os.path.normpath('./Data/distances.txt')
# distances = pd.read_csv(path_distances)

# path_pos_centroids = os.path.normpath('./Data/pos_centroids.txt')
# pos_centroids = pd.read_csv(path_pos_centroids)

# path_pos_stations = os.path.normpath('./Data/pos_stations.txt')
# pos_stations = pd.read_csv(path_pos_stations)

# rayon_exclusif = Parameters.rayon_exclusif
# rayon_walk = Parameters.rayon_walk
# departure_time = Parameters.departure_time
# vitesse_walk = Parameters.vitesse_walk*1000/3600

# # Tri des centroides
# dist_min = []
# centroid_ids = []
# for i in np.unique(distances.centroid_id):
#     dist_min.append(distances.distance.iloc[np.where(distances.centroid_id == i)].sort_values().iloc[0])
#     centroid_ids.append(i)
# df_dist_min = pd.DataFrame()
# df_dist_min['centroid_id'] = centroid_ids
# df_dist_min['distance'] = dist_min
# dist_reduced = df_dist_min.iloc[np.where(df_dist_min.distance <= rayon_exclusif)]
# id_centroid_reduced = [i for i in dist_reduced.centroid_id]

# # Selection des relations WALK
# dists_vf = []
# index_centroid = []
# index_station = []
# longitudes = []
# latitudes = []
# for i in id_centroid_reduced:
#     dists = distances.distance.iloc[np.where(distances.centroid_id == i)].values
#     stations = distances.stop_id.iloc[np.where(distances.centroid_id == i)].values
#     idx_walks = np.where(dists <= rayon_walk)[0]
#     if len(idx_walks) != 0:
#         walk_dists = [dists[k] for k in idx_walks]
#         idx_walks = [np.where(dists == k)[0][0] for k in walk_dists]
#         stations_walks = [stations[k] for k in idx_walks]
#         for j in stations_walks:
#             index_centroid.append(i)
#             longitudes.append(pos_centroids.iloc[np.where(pos_centroids.centroid_id == i)].longitude.iloc[0])
#             latitudes.append(pos_centroids.iloc[np.where(pos_centroids.centroid_id == i)].latitude.iloc[0])
#             index_station.append(j)
#             dists_vf.append(distances.iloc[np.where((distances.centroid_id == i) & (distances.stop_id == j))].distance.iloc[0])
#     else:
#         idx_1000 = np.where(dists <= 6500)[0]
#         min_dist = np.min([dists[i] for i in idx_1000])
#         idx_min = np.where(dists == min_dist)[0]
#         station_min = stations[idx_min][0]
#         index_centroid.append(i)
#         longitudes.append(pos_centroids.iloc[np.where(pos_centroids.centroid_id == i)].longitude.iloc[0])
#         latitudes.append(pos_centroids.iloc[np.where(pos_centroids.centroid_id == i)].latitude.iloc[0])
#         index_station.append(station_min)
#         dists_vf.append(distances.iloc[np.where((distances.centroid_id == i) & (distances.stop_id == station_min))].distance.iloc[0])

# centr = pd.DataFrame()
# centr['centroid_id'] = index_centroid 
# centr['longitude'] = longitudes
# centr['latitude'] = latitudes
# centr['distance'] = dists_vf 
# centr['stop_id'] = index_station

# centroid_vf = pd.DataFrame()
# centroid_vf['centroid_id'] = centr['centroid_id']
# centroid_vf['centroid_lon'] = centr['longitude']
# centroid_vf['centroid_lat'] = centr['latitude']
# centroid_vf['distance'] = round(centr['distance'],3)
# centroid_vf['stop_id'] = centr['stop_id']
# centroid_vf['departure_time'] = [departure_time]*len(centroid_vf)
# centroid_vf['walking_time'] = round(centroid_vf['distance']/vitesse_walk,3)



import numpy as np
import pandas as pd
import Parameters
import time
import os

start_time = time.time()

path_distances = os.path.normpath('./Data/distances.txt')
distances = pd.read_csv(path_distances)

path_pos_centroids = os.path.normpath('./Data/pos_centroids.txt')
pos_centroids = pd.read_csv(path_pos_centroids)

path_pos_stations = os.path.normpath('./Data/pos_stations.txt')
pos_stations = pd.read_csv(path_pos_stations)

rayon_exclusif = Parameters.rayon_exclusif
rayon_walk = Parameters.rayon_walk
departure_time = Parameters.departure_time
vitesse_walk = Parameters.vitesse_walk * 1000 / 3600

# Tri des centroides
df_dist_min = distances.groupby('centroid_id')['distance'].min().reset_index()
dist_reduced = df_dist_min[df_dist_min['distance'] <= rayon_exclusif]
id_centroid_reduced = dist_reduced['centroid_id'].tolist()

id_centroid_reduced
# Selection des relations WALK

# Selection des relations WALK
dists_vf = []
index_centroid = []
index_station = []
longitudes = []
latitudes = []

for i in id_centroid_reduced:
    centroid_data = pos_centroids.loc[pos_centroids['centroid_id'] == i]
    centroid_longitude = centroid_data['longitude'].values[0]
    centroid_latitude = centroid_data['latitude'].values[0]
    
    centroid_distances = distances.loc[distances['centroid_id'] == i]
    walk_distances = centroid_distances.loc[centroid_distances['distance'] <= rayon_walk]
    
    if not walk_distances.empty:
        walk_stations = walk_distances.groupby('centroid_id')['stop_id'].first()
        walk_distances = walk_distances.groupby('centroid_id')['distance'].first()
        
        index_centroid.extend([i] * len(walk_stations))
        longitudes.extend([centroid_longitude] * len(walk_stations))
        latitudes.extend([centroid_latitude] * len(walk_stations))
        index_station.extend(walk_stations)
        dists_vf.extend(walk_distances)
    else:
        min_distance = centroid_distances.loc[centroid_distances['distance'] <= 6500]['distance'].min()
        station_min = centroid_distances.loc[centroid_distances['distance'] == min_distance]['stop_id'].iloc[0]
        
        index_centroid.append(i)
        longitudes.append(centroid_longitude)
        latitudes.append(centroid_latitude)
        index_station.append(station_min)
        dists_vf.append(distances.loc[(distances['centroid_id'] == i) & (distances['stop_id'] == station_min), 'distance'].iloc[0])

centr = pd.DataFrame({
    'centroid_id': index_centroid,
    'longitude': longitudes,
    'latitude': latitudes,
    'distance': dists_vf,
    'stop_id': index_station
})

centroid_vf = pd.DataFrame({
    'centroid_id': centr['centroid_id'],
    'centroid_lon': centr['longitude'],
    'centroid_lat': centr['latitude'],
    'distance': round(centr['distance'], 3),
    'stop_id': centr['stop_id'],
    'departure_time': [departure_time] * len(centr),
    'walking_time': round(centr['distance'] / vitesse_walk, 3)
})

path_centroids = os.path.normpath('./Data/centroids.txt')
centroid_vf.to_csv(path_centroids, index = False) # Fichier 'centroids.txt'

end_time = time.time()
print("temps d'exécution :", end_time - start_time)
print((end_time - start_time)/60, 'minutes')