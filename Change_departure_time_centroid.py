# Le graphe doit deja exister
# efface toutes les relations WALK existantes
# change les 'departure_time' des centroides
# cree les nouvelles relations WALK
import numpy as np
import pandas as pd
import neo4j
from neo4j import GraphDatabase
import Parameters
import os

URI = "bolt://127.0.0.1:7687"
USER = "neo4j"
PASSWORD = "123"

def execute(driver, query):
    """Execute a query."""
    with driver.session() as session:
        if len(query) > 0:
            result = session.run(query)
            return result     
        
query = "MATCH ()-[r:WALK]->() DELETE r"
execute(driver, query)

time = Parameters.new_departure_time

query = "MATCH (c:Centroid) SET c.departure_time = localTime({})".format(time) # change le type en LocalTime Neo4j
execute(driver, query)

path_centroids = os.path.normpath('./Data/centroids.txt')
centroids = pd.read_csv(path_centroids)
centroids['departure_time'] = time
centroids.to_csv(path_centroids, index = False)
centroids = pd.read_csv(path_centroids)
for centr in centroids.iloc:
        print(centr)
        query = "MATCH (c:Centroid), (s:Stoptime) WITH {} AS walking_time, c AS c, s AS s WHERE c.centroid_id = {} AND s.stop_id = toString({}) AND duration.between(localTime('00:00:00'), s.departure_time).seconds >= (duration.between(localTime('00:00:00'), c.departure_time).seconds + walking_time) \n".format(centr['walking_time'], centr['centroid_id'], centr['stop_id'])
        query += "WITH min(s.departure_time) AS min_time, c AS c, walking_time AS walking_time \n"
        query += "MATCH (c), (st:Stoptime) WHERE st.stop_id = toString({}) AND st.departure_time = min_time \n".format(centr['stop_id'])
        query += "CREATE (c)-[r:WALK]->(st) SET r.distance = {} SET r.walking_time = walking_time SET r.inter_time = duration.between(c.departure_time, st.departure_time).seconds".format(round(centr['distance'],3))
        execute(driver, query)
