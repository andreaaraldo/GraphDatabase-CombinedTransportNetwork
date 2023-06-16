import pandas as pd
from datetime import datetime, timedelta


################################################################
#this code is used only to generate stoptimes of a line that is constant , except for a gap of (exact time) between each trip
#therefore, make sure that in stoptimes.txt contains only the detail of 1st trip
#i.e if there are 2 lines, therefore there are only 2 stoptimes detail of the 2 first trips
################################################################
#remark: run this code only once while you have the first trip of each trip.
#otherwise it will generate redundant informations.
################################################################

df_st = pd.read_csv('stop_times.txt')
df_trip=pd.read_csv('trips.txt')

# Initialize an empty list to store all the generated DataFrames
dfs_st = []
dfs_trip=[]

dfs_st.append(df_st)
dfs_trip.append(df_trip)


N=10               #number of trips of each route
hour_offset = 1    # Number of hours to add (in h)

for i in range(N):
    # Create a new DataFrame with modified arrival and departure times and incremented trip_id
    new_df = df_st.copy()  # Copy the original DataFrame
    new_trip=df_trip.copy() 
    
    # Increment the trip_id by 1 for each new trip
    new_df['trip_id'] = new_df['trip_id'].apply(lambda x: x + (i + 1) )
    new_trip['trip_id'] = new_trip['trip_id'].apply(lambda x: x + (i + 1) )
    
    # Add (i+1)*hour_offset hours to the arrival and departure times
    hours_to_add = (i + 1)*hour_offset
    new_df['arrival_time'] = (pd.to_datetime(new_df['arrival_time'], format='%H:%M:%S') + timedelta(hours=hours_to_add)).dt.strftime('%H:%M:%S')
    new_df['departure_time'] = (pd.to_datetime(new_df['departure_time'], format='%H:%M:%S') + timedelta(hours=hours_to_add)).dt.strftime('%H:%M:%S')
    
    # Append the new DataFrame to the list
    dfs_st.append(new_df)
    dfs_trip.append(new_trip)

# Concatenate all the DataFrames in the list
dfs_st = pd.concat(dfs_st)
dfs_trip = pd.concat(dfs_trip)
# trip_id=dfs_st_st["trip_id"].unique()

# print(dfs_trip)


dfs_st.to_csv('stop_times.txt', index=False)
dfs_trip.to_csv('trips.txt', index=False)

