import pandas as pd
import numpy as np
from neo4j import GraphDatabase
import time
import os
import Parameters
import shutil

URI = "bolt://127.0.0.1:7687"
USER = "neo4j"
PASSWORD = "cassiopeedrt"
driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

nb_DRT = Parameters.nb_DRT
Data = Parameters.Data

# Si on veut calculer tous les centroides : mettre True
# False : on calcule les acc pour les centroids qui se trouvent sur une zone de DRT 
calcul_tous_centroids = False

def execute(driver, query): # Exécute une requête Cypher
    """Execute a query."""
    with driver.session() as session:
        if len(query) > 0:
            result = session.run(query)
            return result

def get_res(driver, query): # Récupère le return d'un requête Cypher.
    """Execute a query."""
    with driver.session() as session:
        if len(query) > 0:
            result = session.run(query)
        return [dict(i) for i in result]

def create_graph(): # Sauvegarde le graphe actuel.
    graph = "graphe_{}".format(int(h/60))
    query = "CALL gds.graph.create('{}',".format(graph)     #version No4j 4.0
    query += " '*', '*',{relationshipProperties: 'inter_time'})"
    execute(driver, query)
    
def shortest_path(source_id, target_id): # Cherche le PCC d'une source à une target et retourne le coût (temps en secondes) total du PCC.
    query = "MATCH (source:Centroid), (target:Stop) WHERE source.centroid_id = {} AND target.stop_id = {} \n".format(source_id, target_id)
    query += "CALL gds.shortestPath.dijkstra.stream('graphe_{}',".format(int(h/60))
    query += "{sourceNode: id(source), targetNode: id(target), relationshipWeightProperty: 'inter_time'}) \n"
    query += "YIELD sourceNode, targetNode, totalCost, nodeIds, costs, path \n"
    query += "CALL apoc.algo.cover(nodeIds) YIELD rel WITH startNode(rel) as a, endNode(rel) as b, rel as rel, path AS path, totalCost as totalCost \n"
    query += "RETURN a.stop_id as from, type(rel) as types, b.stop_id as to, rel.inter_time AS inter_times, rel.walking_time AS walking_time, rel.waiting_time AS waiting_DRT, rel.travel_time AS DRT_time, totalCost AS totaltime"
    return query

def get_transport(res):
    trsp = []
    for r in res:
        if (r['types'] == 'DRT') or (r['types'] == 'WALK'):
            trsp.append(r['types'])
    if len(trsp) == 2:
        transport = 'DRT/WALK'
    elif len(trsp) == 1:
        transport = trsp[0]
    else:
        transport = 'None'
    return transport

def get_correspondance_nbr(res):
    tab = [res[i]['types'] for i in range(len(res))]
    i = 0
    for j in tab:
        if j == 'CORRESPONDANCE':
            i += 1
    return i

def get_first_station(res):
    for r in res:
        if (r['types'] == 'DRT') or (r['types'] == 'WALK'):
            return r['to']
        
def get_times_first_station(res):
    intertime = 'None'
    waiting_time = 'None'
    DRT_time = 'None'
    walking_time = 'None'
    for r in res:
        if r['types'] == 'DRT':
            intertime = r['inter_times']
            waiting_time = r['waiting_DRT']
            DRT_time = r['DRT_time']
        if r['types'] == 'WALK':
            walking_time = r['walking_time']
        
    return intertime, walking_time, waiting_time, DRT_time

def get_dataframe(centroid_id): # Crée un dataframe pour chaque centroïde contenant les destinations, le coût total du PCC associé, et le temps de trajet direct à pieds (vol d'oiseau).
    distance = distances[distances['centroid_id'] == centroid_id][['distance', 'stop_id']].reset_index(drop=True)
    #stops_in_radius = distance[ (distance['distance'] <= ray_max) & (distance['distance'] > ray_min)]
    stops_in_radius = distance[ (distance['distance'] <= ray_max)]
    
    destinations = []
    total_times = []
    transport = []
    correspondance = []
    first_station = []
    time_first_station = []
    walking_times = []
    drt_times = []
    drt_waiting_times = []
    direct_walk_times = []
    station_atteintes = []

    for _, stop in stops_in_radius.astype(int).iterrows():
        dist = distance.loc[distance['stop_id'] == stop.stop_id, 'distance'].values[0]
        query = shortest_path(centroid_id, stop.stop_id)
        # print(query)
        results = get_res(driver, query)

        if results:
            station_atteintes.append(stop.stop_id)
            destinations.append(stop['stop_id'])
            total_times.append(results[0]['totaltime'])
            transport.append(get_transport(results))
            correspondance.append(get_correspondance_nbr(results))
            first_station.append(get_first_station(results))
            time, walking_time, waiting_time, drt_time = get_times_first_station(results)
            time_first_station.append(time)
            walking_times.append(walking_time)
            drt_times.append(drt_time)
            drt_waiting_times.append(waiting_time)
        else:
            station_atteintes.append('None')
            destinations.append(stop['stop_id'])
            total_times.append('None')
            transport.append('None')
            correspondance.append('None')
            first_station.append('None')
            time_first_station.append('None')
            walking_times.append('None')
            drt_times.append('None')
            drt_waiting_times.append('None')

        direct_walk_times.append(dist/vitesse_walk)

    df = pd.DataFrame({
        'destination': destinations,
        'total_time': total_times,
        'transport': transport,
        'correspondance': correspondance,
        '1st_station': first_station,
        'time_to_1st_station': time_first_station,
        'walking_time': walking_times,
        'drt_time': drt_times,
        'drt_waiting_time': drt_waiting_times,
        'direct_walk_time': direct_walk_times
    })

    df_infos = pd.DataFrame({
        'station dans rayon': stops_in_radius['stop_id'],
        'station atteintes': station_atteintes
    })
    print('OK')
    return df, df_infos

def dataframe(centroid_id): # Sauvegarde le dataframe dans un fichier.
    print("Saving the dataframe to a file...")
    c, c_infos = get_dataframe(centroid_id)
    path_centroids = os.path.normpath("./Results_{}/h_{}_min_{}DRT{}/centroid_{}.txt".format(Data, int(h/60), nb_DRT, suffix, centroid_id))
    path_centroids_info = os.path.normpath("./Results_{}/h_{}_min_{}DRT{}/centroid_{}_infos.txt".format(Data, int(h/60), nb_DRT, suffix, centroid_id))
    c.to_csv(path_centroids, index=False)
    c_infos.to_csv(path_centroids_info, index=False)
    del c
    del c_infos

###############################################################################
###############################################################################
start_time = time.time()

ray_max = Parameters.ray_max
ray_min = Parameters.ray_min
h = Parameters.h
print("Number of hours : ", h/60)

###############################################################################
# Gestion de dossiers 
###############################################################################

##########
# option 1 : on calcule seulement les accessibilités autour des DRT
###########

#if nb_DRT==0, i.e we calculate all accessibility of all centroids

if nb_DRT==0:
    path_centroids = os.path.join(Data,"centroids.txt")
    centroids = pd.read_csv(path_centroids)['centroid_id'].unique()
    centroids = pd.DataFrame({'centroid_id': centroids})
    path_idstxt = os.path.join("Results_{}".format(Data),"ids.txt")
    centroids.to_csv(path_idstxt, index=False, header=True)


# id des centroides pour lesquelles on calcule l'accessibilite
if calcul_tous_centroids == True :
    suffix = '_all'
    # id des centroides pour lesquelles on calcule l'accessibilite
    path_ids = os.path.normpath("./Results_{}/ids_all.txt".format(Data))

    #création de ids_all
    if not os.path.isdir(path_ids):
        with open(path_ids, "w") as f:
            # Écriture de la première ligne
            f.write("centroid_id\n")
            # Écriture des chiffres de 0 à 1318
            for i in range(1319):
                f.write(str(i) + "\n")
else : 
    suffix = ''
    path_ids = os.path.normpath("./Results_{}/ids.txt".format(Data))

centr = pd.read_csv(path_ids)['centroid_id']
print("centroid_id : ", centr)

path_distances = os.path.normpath("./{}/distances.txt".format(Data))
distances = pd.read_csv(path_distances)
path_stops = os.path.normpath("./{}/stops.txt".format(Data))
stops = pd.read_csv(path_stops)


###############################################################################
#Calcul de PCC
###############################################################################
# Vitesse de marche
vitesse_walk = Parameters.vitesse_walk*1000/3600

# # Sauvegarde l'état du graphe sur lequel on cherche les PCC
create_graph()


#Création du dossier "h_{}_min_{}DRT".format(int(h/60), nb_DRT) dans Results
print("Création du dossier 'h_", int(h/60), "_min")

directory = "h_{}_min_{}DRT{}".format(int(h/60), nb_DRT, suffix)
dir_path = os.path.join('./Results_{}'.format(Data), directory)
directory_old = "h_{}_min_{}DRT{}_old".format(int(h/60), nb_DRT, suffix)
old_dir_path = os.path.join('./Results_{}'.format(Data), directory_old)


#Si le dossier existe, alors on le renome _old et on supprime l'historique
if os.path.isdir(dir_path):
    #on supprime l'historique s'il existe
    if os.path.isdir(os.path.join('./Results_{}'.format(Data), directory_old)):
        shutil.rmtree(old_dir_path)
    #on renome le dossier pour le placer dans l'historique
    os.rename(dir_path, old_dir_path)

dir_path_new = os.path.join('./Results_{}'.format(Data), directory)
os.mkdir(dir_path_new)

# PCC et sauvegarde les temps totaux
for c in centr:
    print('centroid : ', c)
    dataframe(c)

end_time = time.time()
print("Temps d'exécution :", end_time - start_time)
print((end_time - start_time)/60, 'minutes')
#15-20 min