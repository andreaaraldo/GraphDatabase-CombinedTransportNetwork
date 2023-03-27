# Cree le dataframe resumant les infos necessaires sur les trips, routes, stops, stoptimes
# Cree le fichier 'df.txt'
import numpy as np
import pandas as pd
import time

start_time = time.time()

stoptimes = pd.read_csv(r'./Data/stop_times.txt')
trips = pd.read_csv(r'./Data/trips.txt')

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

end_time = time.time()
print("temps d'exécution :", end_time - start_time)
print((end_time - start_time)/60, 'minutes')
