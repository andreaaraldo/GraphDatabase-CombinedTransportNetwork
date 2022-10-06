import pandas as pd
import numpy as np
import winsound
import neo4j
from neo4j import GraphDatabase
import time


URI = "bolt://127.0.0.1:7687"
USER = "neo4j"
PASSWORD = "123"
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
    query += "RETURN totalCost AS totaltime"
    return query


def get_dataframe(centroid_id): # Crée un dataframe pour chaque centroïde contenant les destinations, le coût total du PCC associé, et le temps de trajet direct à pieds (vol d'oiseau).
    distances = pd.read_csv(r".\Data\distances.txt")
    stops = pd.read_csv(r".\Data\stops.txt")
    distance = pd.DataFrame([distances.iloc[i, [1, 2]] for i in np.where(distances.centroid_id == centroid_id)[0]])
    destinations = []
    total_times = []
    direct_walk_times = []
    k = 0
    s = 0
    station_dans_rayon = []
    station_atteintes = []
    for stop in stops.iloc:
        dist = distance.iloc[np.where(distance.stop_id == stop.stop_id)[0][0]].distances
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
            else:
                k += 1
                station_atteintes.append(stop.stop_id)
                destinations.append(stop['stop_id'])
                total_times.append(results[0]['totaltime'])
            direct_walk_times.append(dist/vitesse_walk)
    df = pd.DataFrame()
    df['destination'] = destinations
    df['total_time'] = total_times
    df['direct_walk_time'] = direct_walk_times

    df_infos = pd.DataFrame()
    df_infos['station dans rayon'] = station_dans_rayon
    df_infos['station atteintes'] = station_atteintes

    print('OK')
    return df, df_infos


def dataframe(centroid_id): # Sauvegarde le dataframe dans un fichier.
    c, c_infos = get_dataframe(centroid_id)
    c.to_csv(r".\Results\h_{}_min\centroid_{}.txt".format(int(h/60), centroid_id), index=False)
    c_infos.to_csv(r".\Results\h_{}_min\centroid_{}_infos.txt".format(int(h/60), centroid_id), index=False)
    del c
    del c_infos


###############################################################################

start_time = time.time()

h0 = [60, 120, 240, 960, 1920, 3840]

ray_max = 10000
ray_min = 2000

# # Créer le fichier 'ids.txt' pour h = 1 min avant de changer de valeur de h. Donc graphe h = 1 min.
# h = h0[0]
# query = "MATCH (c:Centroid)-[:DRT]->(st:Stoptime) RETURN c.centroid_id"
# res = get_res(driver, query)
# centr = []
# for i in res:
#     centr.append(i['c.centroid_id'])
# centr = np.unique(centr)
# df_centroids = pd.DataFrame()
# df_centroids['centroid_id'] = centr
# df_centroids.to_csv(r".\Results\h_{}_min\ids.txt".format(int(h/60)), index=False)


# PCC qu'à partir des centroïdes ayant des relations 'DRT'
h = h0[0]
# h = 0
if h == h0[0]:
    query = "MATCH (c:Centroid)-[:DRT]->(st:Stoptime) RETURN c.centroid_id"
    res = get_res(driver, query)
    centr = []
    for i in res:
        centr.append(i['c.centroid_id'])
    centr = np.unique(centr)
else:
    centr = pd.read_csv(r".\Results\h_1_min\ids.txt")['centroid_id']

# Sauver les ids des centroïdes ayant des relations 'DRT'
df_centroids = pd.DataFrame()
df_centroids['centroid_id'] = centr
df_centroids.to_csv(r".\Results\h_{}_min\ids.txt".format(int(h/60)), index=False)

# Vitesse de marche
vitesse_walk = 3*1000/3600

# Créer le graphe sur lequel on cherche les PCC
create_graph()

# PCC et sauvegarde les temps totaux
for c in centr:
    print('centroid : ', c)
    dataframe(c)

end_time = time.time()
print("Temps d'exécution :", end_time - start_time)

winsound.Beep(1000, 1000)
