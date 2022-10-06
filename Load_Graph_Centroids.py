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


def create_df():
    # Crée le dataframe résumant les infos nécessaires sur les trips, routes, stops, stoptimes
    df_routes = []
    for i in range(len(stoptimes)):
        for j in range(len(trips)):
            if stoptimes.trip_id[i] == trips.trip_id[j]:
                df_routes.append(trips.route_id[j])
    df = pd.DataFrame()
    df['trip_id'] = stoptimes.trip_id
    df['arrival_time'] = stoptimes.arrival_time
    df['departure_time'] = stoptimes.departure_time
    df['stop_id'] = stoptimes.stop_id
    df['stop_sequence'] = stoptimes.stop_sequence
    df['route_id'] = df_routes 
    df.to_csv(r".\Data\df.txt", index = False)
    
    
def load_data():
    clean_query = "MATCH (n) DETACH DELETE n" # efface tout le graphe si il y en avait déjà un
    execute(driver, clean_query)
    
    df = pd.read_csv(r".\Data\df.txt")
    
    # Stoptime Nodes
    for st in df.iloc:
        query = "CREATE (st:Stoptime) \n"
        for c in df.columns:
            query += "SET st.{} = toString(\"{}\") \n".format(c, st[c])
        execute(driver, query)
    
    # Types modif (toInteger or toFloat instead of String)
    query = "MATCH (st:Stoptime) SET st.stop_sequence = toInteger(st.stop_sequence) SET st.stop_id = toInteger(st.stop_id) SET st.trip_id = toInteger(st.trip_id) SET st.route_id = toInteger(st.route_id)"
    execute(driver, query)
    
    # Add duration of arrival_time and departure_time :
    query = "MATCH (st:Stoptime) SET st.departure_duration = toInteger(substring(st.departure_time, 0,2))*3600 + toInteger(substring(st.departure_time, 3,2))*60 + toInteger(substring(st.departure_time, 6,2)) SET st.arrival_duration =  toInteger(substring(st.arrival_time, 0,2))*3600 + toInteger(substring(st.arrival_time, 3,2))*60 + toInteger(substring(st.arrival_time, 6,2))"
    execute(driver, query)
    
    # Relationship "PRECEDES" between Stoptime & Stoptime
    query = "MATCH (s1:Stoptime),(s2:Stoptime) WHERE s1.trip_id = s2.trip_id AND s2.stop_sequence = s1.stop_sequence+1 CREATE (s1)-[:PRECEDES]->(s2)"
    execute(driver, query)
    
    # Create property "inter_time" on relationship "PRECEDES"
    query = "MATCH (s1:Stoptime)-[r:PRECEDES]->(s2:Stoptime) SET r.inter_time = s2.departure_duration - s1.arrival_duration"
    execute(driver, query)

    # Create relationship "CORRESPONDANCE"  and its property "inter_time" if "inter_time" is < 24h (86400 sec)
    query = "MATCH (s1:Stoptime),(s2:Stoptime) WHERE s1.stop_id = s2.stop_id AND s1.route_id <> s2.route_id AND s1.arrival_duration < s2.departure_duration AND (s2.departure_duration - s1.arrival_duration) < 86400 CREATE (s1)-[r:CORRESPONDANCE]->(s2) SET r.inter_time = s2.departure_duration - s1.arrival_duration"
    execute(driver, query)
    
    # Stop Nodes
    for s in stops.iloc:
        query = "CREATE (s:Stop) \n"
        for c in stops.columns:
            query += "SET s.{} = toString(\"{}\") \n".format(c, s[c])
        execute(driver, query)
        
    # Type stop_id --> Integer
    query = "MATCH (s:Stop) SET s.stop_id = toInteger(s.stop_id)"
    execute(driver, query)
    
    # Relation LOCATED_AT & property inter_time (= 0)
    query = "MATCH (s:Stop), (st:Stoptime) WHERE s.stop_id = st.stop_id CREATE (s)<-[r:LOCATED_AT]-(st) SET r.inter_time = 0"
    execute(driver, query)
    
    # Create Centroid Nodes
    for centr in np.unique(centroids['centroid_id']):
        query = "CREATE (c:Centroid) \n"
        for c in centroids[['centroid_id', 'centroid_lon', 'centroid_lat', 'departure_time']].columns:
            query += "SET c.{} = {} \n".format(c, centroids[c][np.where(centroids['centroid_id'] == centr)[0][0]])
        execute(driver, query)
        
    # type of time = localTime
    query = "MATCH (c:Centroid) SET c.departure_duration = toInteger(substring(c.departure_time, 0,2))*3600 + toInteger(substring(c.departure_time, 3,2))*60 + toInteger(substring(c.departure_time, 6,2))"
    execute(driver, query)
    
    # Relationship & properties
    ### ~ 30 min ###
    for centr in centroids.iloc:
        print(centr.centroid_id)
        query = "MATCH (c:Centroid), (s:Stoptime) WITH {} AS walking_time, c AS c, s AS s WHERE c.centroid_id = {} AND s.stop_id = {} AND s.departure_duration >= c.departure_duration + walking_time \n".format(centr['walking_time'], centr['centroid_id'], centr['stop_id'])
        query += "WITH min(s.departure_duration) AS min_time, c AS c, walking_time AS walking_time \n"
        query += "MATCH (c), (st:Stoptime) WHERE st.stop_id = {} AND st.departure_duration = min_time \n".format(centr['stop_id'])
        query += "CREATE (c)-[r:WALK]->(st) SET r.distance = {} SET r.walking_time = walking_time SET r.inter_time = st.departure_duration - c.departure_duration".format(round(centr['distance'],3))
        execute(driver, query)
    

###############################################################################

routes = pd.read_csv(r".\Data\routes.txt")
trips = pd.read_csv(r".\Data\trips.txt")
stops = pd.read_csv(r".\Data\stops.txt")
stoptimes = pd.read_csv(r".\Data\stop_times.txt")
centroids = pd.read_csv(r".\Data\centroids.txt")

# create_df()

start_time = time.time()
load_data()
end_time = time.time()
print("temps d'exécution :", end_time - start_time)
print((end_time - start_time)/60, 'minutes')
