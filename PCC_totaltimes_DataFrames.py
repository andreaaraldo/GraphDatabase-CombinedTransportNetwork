import pandas as pd
import numpy as np
import neo4j
from neo4j import GraphDatabase
import time
import os
import Parameters

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
    with driver.session() as session:
        if len(query) > 0:
            result = session.run(query)
        return [dict(i) for i in result]

def create_graph(): # Sauvegarde le graphe actuel.
    graph = "graphe_{}".format(int(h/60))
    query = "CALL gds.graph.create('{}',".format(graph)
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
    a = 0
    trsp = []
    for r in res:
        if (r['types'] == 'DRT') or (r['types'] == 'WALK'):
            trsp.append(r['types'])
            a += 1
    if a == 2:
        transport = 'DRT/WALK'
    else:
        transport = trsp[0]
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
    distances = pd.read_csv(r".\Data\distances.txt")
    stops = pd.read_csv(r".\Data\stops.txt")
    distance = pd.DataFrame([distances.iloc[i, [1, 2]] for i in np.where(distances.centroid_id == centroid_id)[0]])
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
    k = 0
    s = 0
    station_dans_rayon = []
    station_atteintes = []
    for stop in stops.iloc:
        dist = distance.iloc[np.where(distance.stop_id == stop.stop_id)[0][0]].distance
        # Si la station se trouvent entre les rayons de 2 et 10 km du centroïde
        if (dist <= ray_max) & (dist > ray_min):
            s += 1
            station_dans_rayon.append(stop.stop_id)
            query = shortest_path(centroid_id, stop.stop_id)
            results = get_res(driver, query)
            # S'il n'existe pas de chemin (les horaires ne concordent pas)
            if results == []:
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
            else:
                k += 1
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
            direct_walk_times.append(dist/vitesse_walk)
    df = pd.DataFrame()
    df['destination'] = destinations
    df['total_time'] = total_times
    df['transport'] = transport
    df['correspondance'] = correspondance
    df['1st_station'] = first_station
    df['time_to_1st_station'] = time_first_station
    df['walking_time'] = walking_times
    df['drt_time'] = drt_times
    df['drt_waiting_time'] = drt_waiting_times
    df['direct_walk_time'] = direct_walk_times

    df_infos = pd.DataFrame()
    df_infos['station dans rayon'] = station_dans_rayon
    df_infos['station atteintes'] = station_atteintes

    print('OK')
    return df, df_infos

def dataframe(centroid_id): # Sauvegarde le dataframe dans un fichier.
    c, c_infos = get_dataframe(centroid_id)
    c.to_csv(r"./Results/h_{}_min/centroid_{}.txt".format(int(h/60), centroid_id), index=False)
    c_infos.to_csv(r"./Results/h_{}_min/centroid_{}_infos.txt".format(int(h/60), centroid_id), index=False)
    del c
    del c_infos
###############################################################################
start_time = time.time()

ray_max = Parameters.ray_max
ray_min = Parameters.ray_min
h = Parameters.h

# id des centroides pour lesquelles on calcule l'accessibilite
centr = pd.read_csv(r"./Results/ids.txt")['centroid_id']

# Vitesse de marche
vitesse_walk = Parameters.vitesse_walk*1000/3600

# # Sauvegarde l'état du graphe sur lequel on cherche les PCC
create_graph()

directory = "h_{}_min".format(int(h/60))
parent_dir = ".\Results"
path = os.path.join(parent_dir, directory)
os.mkdir(path)

# PCC et sauvegarde les temps totaux
for c in centr:
    print('centroid : ', c)
    dataframe(c)

end_time = time.time()
print("Temps d'exécution :", end_time - start_time)
print((end_time - start_time)/60, 'minutes')
