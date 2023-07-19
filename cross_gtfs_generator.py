import pandas as pd
import pandas as pd
import os
from datetime import datetime, timedelta

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Initialize DataFrames for each GTFS entity
agencies_df = pd.DataFrame(columns=['agency_id', 'agency_name', 'agency_timezone', 'agency_url'])
calendar_df = pd.DataFrame(columns=['service_id', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'start_date', 'end_date'])
routes_df = pd.DataFrame(columns=['agency_id', 'route_id', 'route_long_name', 'route_short_name'])
stops_df = pd.DataFrame(columns=['stop_id', 'stop_lat', 'stop_lon', 'stop_name', 'wheelchair_boarding', 'zone_id'])
stop_times_df = pd.DataFrame(columns=['trip_id', 'arrival_time', 'departure_time', 'stop_id', 'stop_sequence', 'stop_headsign', 'shape_dist_traveled'])
trips_df = pd.DataFrame(columns=['route_id', 'service_id', 'trip_id', 'trip_headsign', 'trip_short_name', 'direction_id', 'block_id'])

def add_agency(agency_id, agency_name, agency_timezone, agency_url):
    global agencies_df
    agencies_df = agencies_df.append({
        'agency_id': agency_id,
        'agency_name': agency_name,
        'agency_timezone': agency_timezone,
        'agency_url': agency_url
    }, ignore_index=True)

def add_calendar(service_id, monday, tuesday, wednesday, thursday, friday, saturday, sunday, start_date, end_date):
    global calendar_df
    calendar_df = calendar_df.append({
        'service_id': service_id,
        'monday': monday,
        'tuesday': tuesday,
        'wednesday': wednesday,
        'thursday': thursday,
        'friday': friday,
        'saturday': saturday,
        'sunday': sunday,
        'start_date': start_date,
        'end_date': end_date
    }, ignore_index=True)

def add_route(agency_id, route_id, route_long_name, route_short_name):
    global routes_df
    routes_df = routes_df.append({
        'agency_id': agency_id,
        'route_id': route_id,
        'route_long_name': route_long_name,
        'route_short_name': route_short_name
    }, ignore_index=True)

def add_stop(stop_id, stop_lat, stop_lon, stop_name, wheelchair_boarding, zone_id):
    global stops_df
    stops_df = stops_df.append({
        'stop_id': stop_id,
        'stop_lat': stop_lat,
        'stop_lon': stop_lon,
        'stop_name': stop_name,
        'wheelchair_boarding': wheelchair_boarding,
        'zone_id': zone_id
    }, ignore_index=True)


def add_trip(route_id, service_id, trip_id, trip_headsign, trip_short_name, direction_id, block_id):
    global trips_df
    trips_df = trips_df.append({
        'route_id': route_id,
        'service_id': service_id,
        'trip_id': trip_id,
        'trip_headsign': trip_headsign,
        'trip_short_name': trip_short_name,
        'direction_id': direction_id,
        'block_id': block_id
    }, ignore_index=True)

def add_stoptime(trip_id, arrival_time, departure_time, stop_id, stop_sequence, stop_headsign, shape_dist_traveled):
    global stop_times_df
    stop_times_df = stop_times_df.append({
        'trip_id': trip_id,
        'arrival_time': arrival_time,
        'departure_time': departure_time,
        'stop_id': stop_id,
        'stop_sequence': stop_sequence,
        'stop_headsign': stop_headsign,
        'shape_dist_traveled': shape_dist_traveled
    }, ignore_index=True)

def regenerate_stoptime_with_frequency(N,hour_offset):

    # stops_df = pd.read_csv('stop_times.txt')
    # trips_df=pd.read_csv('trips.txt')
    global stop_times_df,trips_df 

    # Initialize an empty list to store all the generated DataFrames
    dfs_st = []
    dfs_trip=[]

    dfs_st.append(stop_times_df)
    dfs_trip.append(trips_df)

    for i in range(N):
        # Create a new DataFrame with modified arrival and departure times and incremented trip_id
        new_df = stop_times_df.copy()  # Copy the original DataFrame
        new_trip=trips_df.copy() 
        
        # Increment the trip_id by 1 for each new trip
        new_df['trip_id'] = new_df['trip_id'].apply(lambda x: int(x) + (i + 1) )
        new_trip['trip_id'] = new_trip['trip_id'].apply(lambda x: int(x) + (i + 1) )
        
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

    # print(dfs_trip)

    stop_times_df = dfs_st
    trips_df = dfs_trip



def write_gtfs_files():
    global agencies_df, calendar_df, routes_df, stops_df, stop_times_df, trips_df
    # Write DataFrames to CSV files
    agencies_df.to_csv('small_instance/agency.txt', index=False)
    calendar_df.to_csv('small_instance/calendar.txt', index=False)
    routes_df.to_csv('small_instance/routes.txt', index=False)
    stops_df.to_csv('small_instance/stops.txt', index=False)
    stop_times_df.to_csv('small_instance/stop_times.txt', index=False)
    trips_df.to_csv('small_instance/trips.txt', index=False)

# # Distances Centroid-Stop
# def dist(p1, p2): # fonction pour calculer la distance entre 2 points geometriques
#     d = geod.Inverse(p1.y, p1.x, p2.y, p2.x)
#     dist = d['s12']
#     return dist

################################################################

if not os.path.exists('small_instance'):
    os.makedirs('small_instance')


add_agency('ABC', 'ABC', 'America/New_York', 'http://www.example.com')
add_calendar('1', 1, 1, 1, 1, 1, 0, 0, '20230101', '20231231')

D = 1  # distance between each stops in kilometers
bus_speed_kmph = 20

# 2 lines : vertical and horizontal line 
add_route('ABC', '1', 'Vertical Route', 'VERT')
add_route('ABC', '2', 'Horizontal Route', 'HORZ')

# the intersect stop
latitude = 40.7128
longitude = -74.0060

stop_vertical = []
stop_horizontal = []
#create stops for vertical 
for i in range(11):
    stop_id = 1000+i
    stop_vertical.append(stop_id)
    stop_name = f'Stop {stop_id}'
    stop_lat = latitude + (i-5) * 0.0089972
    stop_lon = longitude
    wheelchair_boarding = 1
    zone_id = 'Zone'
    add_stop(stop_id, stop_lat, stop_lon, stop_name, wheelchair_boarding, zone_id)

#create stops for horizotal
for i in range(11):
    if (i!=5):    #redundant the intersect point
        stop_id = 2000+i
        stop_horizontal.append(stop_id)
        stop_name = f'Stop {stop_id}'
        stop_lat = latitude 
        stop_lon = longitude+ (i-5) * 0.012852
        wheelchair_boarding = 1
        zone_id = 'Zone'
        add_stop(stop_id, stop_lat, stop_lon, stop_name, wheelchair_boarding, zone_id)
    else:
        stop_horizontal.append('1005')

start_time = datetime.strptime("08:00:00", '%H:%M:%S')

add_trip('1', '1', "1000", 'Trip', '', 0, '')   
i=0
for st_id in stop_vertical:
    t=start_time+ i*timedelta(minutes=round(D*60/bus_speed_kmph ))
    add_stoptime('1', f'{t:%H:%M:%S}', f'{t:%H:%M:%S}', st_id, i + 1, '', '')
    i+=1

add_trip('2', '1', "2000", 'Trip', '', 0, '')
i=0   
for st_id in stop_horizontal:
    t=start_time+ i*timedelta(minutes=round(D*60/bus_speed_kmph))
    add_stoptime('2', f'{t:%H:%M:%S}', f'{t:%H:%M:%S}', st_id, i + 1, '', '') 
    i+=1

regenerate_stoptime_with_frequency(10,1)

# Write GTFS files
write_gtfs_files()

