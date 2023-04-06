# Cree le dataframe resumant les infos necessaires sur les trips, routes, stops, stoptimes
# Cree le fichier 'df.txt'
import numpy as np
import pandas as pd
import time
import os

start_time = time.time()
#1.35 min

path_stoptimes = os.path.normpath('./Data/stop_times.txt')
stoptimes = pd.read_csv(path_stoptimes)
path_trips = os.path.normpath('./Data/trips.txt')
trips = pd.read_csv(path_trips)

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

path_df = os.path.normpath("./Data/df.txt")
df.to_csv(path_df, index = False) 

end_time = time.time()
print("temps d'exécution :", end_time - start_time)
print((end_time - start_time)/60, 'minutes')
