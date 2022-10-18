# Cree le graphe dans Neo4j
import numpy as np
import neo4j
import pandas as pd
from neo4j import GraphDatabase
import time

URI = "bolt://127.0.0.1:7687"
USER = "neo4j"
PASSWORD = "123"
driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

def execute(driver, query):
    """Execute a query."""
    with driver.session() as session:
        if len(query) > 0:
            result = session.run(query)
            return result   
    
def load_data():
    clean_query = "MATCH (n) DETACH DELETE n" # efface tout le graphe si il y en avait déjà un
    execute(driver, clean_query)
    
    df = pd.read_csv(r".\Data\df.txt")
    # Cree les noeuds Stoptime
    for st in df.iloc:
        query = "CREATE (st:Stoptime) \n"
        for c in df.columns:
            query += "SET st.{} = toString(\"{}\") \n".format(c, st[c])
        execute(driver, query)
    # Modification des types (toInteger ou toFloat au lieu de String)
    query = "MATCH (st:Stoptime) SET st.stop_sequence = toInteger(st.stop_sequence) SET st.stop_id = toInteger(st.stop_id) SET st.trip_id = toInteger(st.trip_id) SET st.route_id = toInteger(st.route_id)"
    execute(driver, query)
    # Ajoute les durees (en secondes) des horaires d'arrivee ou de depart :
    query = "MATCH (st:Stoptime) SET st.departure_duration = toInteger(substring(st.departure_time, 0,2))*3600 + toInteger(substring(st.departure_time, 3,2))*60 + toInteger(substring(st.departure_time, 6,2)) SET st.arrival_duration =  toInteger(substring(st.arrival_time, 0,2))*3600 + toInteger(substring(st.arrival_time, 3,2))*60 + toInteger(substring(st.arrival_time, 6,2))"
    execute(driver, query)
    # Cree les relations PRECEDES entre Stoptimes
    query = "MATCH (s1:Stoptime),(s2:Stoptime) WHERE s1.trip_id = s2.trip_id AND s2.stop_sequence = s1.stop_sequence+1 CREATE (s1)-[:PRECEDES]->(s2)"
    execute(driver, query)
    # Cree les proprietes 'inter_time' sur les relations PRECEDES
    query = "MATCH (s1:Stoptime)-[r:PRECEDES]->(s2:Stoptime) SET r.inter_time = s2.departure_duration - s1.arrival_duration"
    execute(driver, query)
    # Cree les relations "CORRESPONDANCE" et leur propriete 'inter_time' si 'inter_time' est < 24h (86400 sec)
    query = "MATCH (s1:Stoptime),(s2:Stoptime) WHERE s1.stop_id = s2.stop_id AND s1.route_id <> s2.route_id AND s1.arrival_duration < s2.departure_duration AND (s2.departure_duration - s1.arrival_duration) < 86400 CREATE (s1)-[r:CORRESPONDANCE]->(s2) SET r.inter_time = s2.departure_duration - s1.arrival_duration"
    execute(driver, query)
    # Cree les noeuds Stop
    for s in stops.iloc:
        query = "CREATE (s:Stop) \n"
        for c in stops.columns:
            query += "SET s.{} = toString(\"{}\") \n".format(c, s[c])
        execute(driver, query)
    # Type de la propriete'stop_id' --> Integer
    query = "MATCH (s:Stop) SET s.stop_id = toInteger(s.stop_id)"
    execute(driver, query)
    # Cree les relations LOCATED_AT et leur propriete 'inter_time' (= 0)
    query = "MATCH (s:Stop), (st:Stoptime) WHERE s.stop_id = st.stop_id CREATE (s)<-[r:LOCATED_AT]-(st) SET r.inter_time = 0"
    execute(driver, query)
    # Cree les noeuds Centroid
    for centr in np.unique(centroids['centroid_id']):
        query = "CREATE (c:Centroid) \n"
        for c in centroids[['centroid_id', 'centroid_lon', 'centroid_lat', 'departure_time']].columns:
            query += "SET c.{} = {} \n".format(c, centroids[c][np.where(centroids['centroid_id'] == centr)[0][0]])
        execute(driver, query)
    # Ajoute la duree des horaires de depart des centroides
    query = "MATCH (c:Centroid) SET c.departure_duration = toInteger(substring(c.departure_time, 0,2))*3600 + toInteger(substring(c.departure_time, 3,2))*60 + toInteger(substring(c.departure_time, 6,2))"
    execute(driver, query)
    # Cree les relations WALK et leur proprietes
    for centr in centroids.iloc:
        query = "MATCH (c:Centroid), (s:Stoptime) WITH {} AS walking_time, c AS c, s AS s WHERE c.centroid_id = {} AND s.stop_id = {} AND s.departure_duration >= c.departure_duration + walking_time \n".format(centr['walking_time'], centr['centroid_id'], centr['stop_id'])
        query += "WITH min(s.departure_duration) AS min_time, c AS c, walking_time AS walking_time \n"
        query += "MATCH (c), (st:Stoptime) WHERE st.stop_id = {} AND st.departure_duration = min_time \n".format(centr['stop_id'])
        query += "CREATE (c)-[r:WALK]->(st) SET r.distance = {} SET r.walking_time = walking_time SET r.inter_time = st.departure_duration - c.departure_duration".format(round(centr['distance'],3))
        execute(driver, query)    
    # Ajout des indexes sur les stops et les centroides
    query = "CREATE INDEX index_centroid FOR (n:Centroid) ON (n.centroid_id)"
    execute(driver, query)
    query = "CREATE INDEX index_stop FOR (n:Stop) ON (n.stop_id)"
    execute(driver, query)
###############################################################################
stops = pd.read_csv(r".\Data\stops.txt")
centroids = pd.read_csv(r".\Data\centroids.txt")

start_time = time.time()

load_data()

end_time = time.time()
print("temps d'exécution :", end_time - start_time)
print((end_time - start_time)/60, 'minutes')
