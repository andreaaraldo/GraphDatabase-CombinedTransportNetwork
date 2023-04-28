# Cree le graphe dans Neo4j
import numpy as np
import neo4j
import pandas as pd
from neo4j import GraphDatabase
import time
import os

URI = "bolt://127.0.0.1:7687"
USER = "neo4j"
PASSWORD = "cassiopeedrt"
driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
# driver = GraphDatabase.driver(URI)
print(driver)


def execute(driver, query):
    """Execute a query."""
    with driver.session() as session:
        if len(query) > 0:
            result = session.run(query)
            return result   


def bulk_import():
    print('Loading data... \n \n')
    print('Deletes graph if one existed...')
    clean_query = "MATCH (n) DETACH DELETE n" # efface tout le graphe si il y en avait déjà un
    execute(driver, clean_query)
    print('done \n')

    #add the stops
    
    query="""
        LOAD CSV WITH HEADERS FROM 'file:///Data/stops.txt' AS row
        create (s:Stop {
            stop_id: toInteger(row.stop_id),
            stop_code: row.stop_code,
            stop_name: row.stop_name,
            stop_desc: row.stop_desc,
            stop_lat: row.stop_lat,
            stop_lon: row.stop_lon
        })
    """
    execute(driver, query)

    #add the StopTimes and add relationship "Located at" with attribut inter_time=0
    # :auto

    query = """
        USING PERIODIC COMMIT
        LOAD CSV WITH HEADERS FROM 'Data/df.txt' AS row
        match (s:Stop {id: row.stop_id})
        CREATE (st:StopTime {
            arrival_time: row.arrival_time,
            departure_time: row.departure_time,
            arrival_duration: duration({hours:toInteger(split(row.arrival_time, ':')[0]), minutes:toInteger(split(row.arrival_time, ':')[1]), seconds:toInteger(split(row.arrival_time, ':')[2])}),
            departure_duration: duration({hours:toInteger(split(row.departure_time, ':')[0]), minutes:toInteger(split(row.departure_time, ':')[1]), seconds:toInteger(split(row.departure_time, ':')[2])}),
            stop_id: row.stop_id,
            stop_sequence: toInteger(row.stop_sequence,
            route_id: row.route_id
            })-[r:LOCATED_AT]->(s)
        SET r.inter_time = 0;
    """
    execute(driver, query)

    #connect the StopTime sequences
    query="""
        call apoc.periodic.iterate(
        'match (st:StopTime) with st order by st.stop_sequence asc
        with collect(st) as stops
        unwind range(0, size(stops)-2) as i
        with stops[i] as curr, stops[i+1] as next
        merge (curr)-[r:PRECEDES]->(next)
        SET r.inter_time = next.departure_duration - curr.arrival_duration', 
        {batchmode: "BATCH", parallel:true, parallel:true, batchSize:1});
    """
    execute(driver, query)



    print('Creating the "CORRESPONDANCE" relations and their "inter_time" property if "inter_time" is < 24h... ')
    # Cree les relations "CORRESPONDANCE" et leur propriete 'inter_time' si 'inter_time' est < 24h (86400 sec)
    query = "MATCH (s1:Stoptime),(s2:Stoptime) WHERE s1.stop_id = s2.stop_id AND s1.route_id <> s2.route_id AND s1.arrival_duration < s2.departure_duration AND (s2.departure_duration - s1.arrival_duration) < 86400 CREATE (s1)-[r:CORRESPONDANCE]->(s2) SET r.inter_time = s2.departure_duration - s1.arrival_duration"
    execute(driver, query)
    print('done \n')

    #add centroids and relationship WALK
    query="""
        LOAD CSV WITH HEADERS FROM 'Data/centroid.txt' AS row

        MERGE (c:Centroid {centroid_id: row.centroid_id})
        ON CREATE 
            SET c.centroid_lon=row.centroid_lon,
            c.centroid_lat=row.centroid_lat,
            c.departure_time=row.centroid_departure_time,
            c.departure_duration: duration({hours:toInteger(split(row.departure_time, ':')[0]), minutes:toInteger(split(row.departure_time, ':')[1]), seconds:toInteger(split(row.departure_time, ':')[2])}),
        
        WITH c, row
        MATCH (st:StopTime {stop_id: toInteger(row.stop_id)}) 
        WHERE st.departure_duration >= c.departure_duration + row.walking_time
        WITH c, st ORDER BY st.departure_duration LIMIT 1
        CREATE (st)<-[r:WALK {walking_time: toInteger(row.walking_time)}]-(c)
            SET r.distance = row.distance 
            r.walking_time = row.walking_time 
            r.inter_time = st.departure_duration - c.departure_duration;
    """
    execute(driver, query)


    print("Adding indexes on stops and centroids...")
    # Ajout des indexes sur les stops et les centroides
    query = "CREATE INDEX index_centroid FOR (n:Centroid) ON (n.centroid_id)"
    execute(driver, query)
    query = "CREATE INDEX index_stop FOR (n:Stop) ON (n.stop_id)"
    execute(driver, query)
    print('done \n')


########################################################################
path_stops = os.path.normpath("./Data/stops.txt")
stops = pd.read_csv(path_stops)

path_centroids = os.path.normpath("./Data/centroids.txt")
centroids = pd.read_csv(path_centroids)

start_time = time.time()
print("début : ", start_time)

# load_data()
bulk_import()

end_time = time.time()
print("temps d'exécution :", end_time - start_time)
print((end_time - start_time)/60, 'minutes')
#27 min
