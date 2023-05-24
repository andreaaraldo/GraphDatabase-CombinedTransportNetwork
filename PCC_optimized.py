import pandas as pd
import numpy as np
import neo4j
from neo4j import GraphDatabase
import time
import os
import Parameters
import shutil

URI = "bolt://127.0.0.1:7687"
USER = "neo4j"
PASSWORD = "cassiopeedrt"
driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

def execute(driver, query): # Exécute une requête Cypher
    """Execute a query."""
    with driver.session() as session:
        if len(query) > 0:
            result = session.run(query)
            return result

def get_res(driver, query): # Récupère le return d'un requête Cypher.
    """Execute a query."""
    start_time_gr = time.time()
    with driver.session() as session:
        if len(query) > 0:
            result = session.run(query)
        return [dict(i) for i in result]
    end_time_gr = time.time()
    print('get_res : ', start_time_gr - end_time_gr)

def create_graph(): # Sauvegarde le graphe actuel.
    graph = "graphe_{}".format(int(h/60))
    query = "CALL gds.graph.create('{}',".format(graph)     #version No4j 4.0
    # query = "CALL gds.graph.project('{}',".format(graph)     #version No4j 5.5
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
    stops_in_radius = stops[(stops['stop_id'].isin(distance['stop_id'])) & (distance['distance'] <= ray_max) & (distance['distance'] > ray_min)]

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

    for _, stop in stops_in_radius.iterrows():
        dist = distance.loc[distance['stop_id'] == stop.stop_id, 'distance'].values[0]
        query = shortest_path(centroid_id, stop.stop_id)
        print(query)
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
        'station atteintes': destinations
    })

    print('OK')
    return df, df_infos

def dataframe(centroid_id): # Sauvegarde le dataframe dans un fichier.
    print("Saving the dataframe to a file...")
    c, c_infos = get_dataframe(centroid_id)
    path_centroids = os.path.normpath("./Results/h_{}_min/centroid_{}.txt".format(int(h/60), centroid_id))
    path_centroids_info = os.path.normpath("./Results/h_{}_min/centroid_{}_infos.txt".format(int(h/60), centroid_id))
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
# id des centroides pour lesquelles on calcule l'accessibilite
path_ids = os.path.normpath("./Results/ids.txt")
centr = pd.read_csv(path_ids)['centroid_id']
print("centroid_id : ", centr)

path_distances = os.path.normpath("./Data/distances.txt")
distances = pd.read_csv(path_distances)
path_stops = os.path.normpath("./Data/stops.txt")
stops = pd.read_csv(path_stops)

###############################################################################
#Calcul de PCC
###############################################################################
# Vitesse de marche
vitesse_walk = Parameters.vitesse_walk*1000/3600

# # Sauvegarde l'état du graphe sur lequel on cherche les PCC
create_graph()


#Création du dossier "h_{}_min".format(int(h/60)) dans Results
print("Création du dossier 'h_",int(h/60),"_min'")

directory = "h_{}_min".format(int(h/60))
dir_path = os.path.join('./Results', directory)
directory_old = "h_{}_min_old".format(int(h/60))
old_dir_path = os.path.join('./Results', directory_old)


#Si le dossier existe, alors on le renome _old et on supprime l'historique
if os.path.isdir(dir_path):
    #on supprime l'historique s'il existe
    if os.path.isdir(os.path.join("./Results", directory_old)):
        shutil.rmtree(old_dir_path)
    #on renome le dossier pour le placer dans l'historique
    os.rename(dir_path, old_dir_path)

dir_path_new = os.path.join('./Results', directory)
os.mkdir(dir_path_new)

# PCC et sauvegarde les temps totaux
for c in centr:
    print('centroid : ', c)
    dataframe(c)

end_time = time.time()
print("Temps d'exécution :", end_time - start_time)
print((end_time - start_time)/60, 'minutes')

#15-20 min