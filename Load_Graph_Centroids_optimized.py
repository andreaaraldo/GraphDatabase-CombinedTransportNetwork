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



"""
in order to use load_csv with local files, make sure to do as follows:

1.Find the neo4j.conf file for your Neo4j installation. Read here about file locations.

2.Comment this line(By adding # in the start):
dbms.directories.import=import

3.Uncomment this line to allow CSV import from file URL:
#dbms.security.allow_csv_import_from_file_urls=true

4.Restart Neo4j
"""

def import_using_load_csv():

    curr_directory = os.getcwd() #get current directory i.e GraphDatabase-combinedtransportnetworks

    print('Loading data... \n \n')
    print('Deletes graph if one existed...')
    clean_query = "MATCH (n) DETACH DELETE n" # efface tout le graphe si il y en avait déjà un
    execute(driver, clean_query)
    try:
        clean_query = "DROP INDEX ON :Centroid(centroid_id)"
        execute(driver, clean_query)
        clean_query = "DROP INDEX ON :Stop(stop_id)"
        execute(driver, clean_query)
    except:
        print("Index does not exist")
    
    print('done \n')

    #add the stops
    print("Adding stops..\n\n")
    path_stops = os.path.normpath("{}/Data/stops.txt".format(curr_directory))
    
    query="""
        LOAD CSV WITH HEADERS FROM 'file:///{}' AS row
        CREATE (s:Stop {{stop_id: toInteger(row.stop_id),
            stop_code: row.stop_code,
            stop_name: row.stop_name,
            stop_desc: row.stop_desc,
            stop_lat: row.stop_lat,
            stop_lon: row.stop_lon
        }})
    """.format(path_stops)
    #print(query)
    execute(driver, query)
    print("done \n")

 
    #add the Stoptimes and add relationship "Located at" with attribut inter_time=0
    print("Adding Stoptimes and Relationship LOCATED AT ..\n\n")
    path_df = os.path.normpath("{}/Data/df.txt".format(curr_directory))
    query = """
        using periodic commit
        LOAD CSV WITH HEADERS FROM 'file:///"""+path_df+"""' AS row
        MATCH (s:Stop {stop_id: toInteger(row.stop_id)})
        CREATE (st:Stoptime {
            trip_id: toInteger(row.trip_id),
            arrival_time: row.arrival_time,
            departure_time: row.departure_time,
            arrival_duration: toInteger(substring(row.arrival_time, 0,2))*3600 + toInteger(substring(row.arrival_time, 3,2))*60 + toInteger(substring(row.arrival_time, 6,2)),
            departure_duration: toInteger(substring(row.departure_time, 0,2))*3600 + toInteger(substring(row.departure_time, 3,2))*60 + toInteger(substring(row.departure_time, 6,2)),
            stop_id: toInteger(row.stop_id),
            stop_sequence: toInteger(row.stop_sequence),
            route_id: toInteger(row.route_id)
            }) -[r:LOCATED_AT]->(s)
        SET r.inter_time = 0;
    """
    #print(query)
    execute(driver, query)
    print("done \n")


    #connect the Stoptime sequences (ralation PRECEDES)
    print("connect the Stoptime sequences (ralation PRECEDES)..\n\n")
    query = "MATCH (s1:Stoptime),(s2:Stoptime) WHERE s1.trip_id = s2.trip_id AND s2.stop_sequence = s1.stop_sequence+1 CREATE (s1)-[:PRECEDES]->(s2)"
    execute(driver, query)
    query = "MATCH (s1:Stoptime)-[r:PRECEDES]->(s2:Stoptime) SET r.inter_time = s2.departure_duration - s1.arrival_duration"
    execute(driver, query)
    # query="""
    #     call apoc.periodic.iterate(
    #     'MATCH (s1:Stoptime) RETURN DISTINCT s1.trip_id as trip_id',
    #     'match (st:Stoptime {trip_id: trip_id}) with st order by st.stop_sequence asc
    #     with collect(st) as stops
    #     unwind range(0, size(stops)-2) as i
    #     with stops[i] as curr, stops[i+1] as next
    #     merge (curr)-[r:PRECEDES]->(next)
    #     SET r.inter_time = next.departure_duration - curr.arrival_duration', 
    #     {batchmode: "BATCH", parallel:true, parallel:true, batchSize:100});
    # """

    print("done \n")



    print('Creating the "CORRESPONDANCE" relations and their "inter_time" property if "inter_time" is < 24h.....\n\n ')
    # Cree les relations "CORRESPONDANCE" et leur propriete 'inter_time' si 'inter_time' est < 24h (86400 sec)
    query = """
        MATCH (s1:Stoptime),(s2:Stoptime) 
        WHERE s1.stop_id = s2.stop_id AND s1.route_id <> s2.route_id AND s1.arrival_duration < s2.departure_duration AND (s2.departure_duration - s1.arrival_duration) < 86400 
        Merge (s1)-[r:CORRESPONDANCE]->(s2) SET r.inter_time = s2.departure_duration - s1.arrival_duration"""
    execute(driver, query)
    print('done \n')

    print('Add centroids and relations WALK..\n\n')
    #add centroids and relationship WALK
    path_centroids=os.path.normpath("{}/Data/centroids.txt".format(curr_directory))
    query="""
        LOAD CSV WITH HEADERS FROM 'file:///"""+path_centroids+"""' AS row
        MERGE (c:Centroid {centroid_id: toInteger(row.centroid_id)})
        ON CREATE 
            SET c.centroid_lon=row.centroid_lon,
            c.centroid_lat=row.centroid_lat,
            c.departure_time=substring(row.departure_time, 1, 2) + ':' + substring(row.departure_time, 4, 2) + ':' + substring(row.departure_time, 7, 2),
            c.departure_duration= toInteger(substring(row.departure_time, 1, 2))*3600 + toInteger(substring(row.departure_time, 4, 2))*60 + toInteger(substring(row.departure_time, 7, 2))
        WITH c,row, toInteger(row.walking_time) as walking_time
        MATCH (st:Stoptime {stop_id: toInteger(row.stop_id)}) 
        WHERE st.departure_duration >= c.departure_duration + walking_time
        WITH c, st,min(st.departure_duration) as min,row
        order by st.departure_duration, min
        WITH row, COLLECT(st) AS Sts, c
        WITH row, Sts[0] AS minSt, c
        CREATE (minSt)<-[r:WALK ]-(c)
            SET r.distance = toInteger(row.distance )
            set r.walking_time = toInteger(row.walking_time )
            set r.inter_time = minSt.departure_duration - c.departure_duration;
    """
    #print(query)
    execute(driver, query)
    print("done \n")


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
import_using_load_csv()

end_time = time.time()
print("temps d'exécution :", end_time - start_time)
print((end_time - start_time)/60, 'minutes')
#1 min
