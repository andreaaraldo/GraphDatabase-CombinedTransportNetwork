import numpy as np
import pandas as pd
import matplotlib as matplotlib
import matplotlib.pyplot as plt
import time
from pyproj import Geod
from shapely.geometry import Polygon, LineString, Point
import Parameters
import os
import shutil
import sys

def get_stations_df():
    stations0 = []
    for i in range(len(stops)):
        stations0.append(Point(stops.stop_lon[i], stops.stop_lat[i]))
    stations = pd.DataFrame()
    stations['stop_id'] = stops.stop_id
    stations['station'] = [i for i in stations0]
    return stations

def choose(id_station, show): 

    station = stations.iloc[np.where(stations.stop_id == id_station)[0][0]]
    A = Point(station.station.x, station.station.y) # Les coordonnées de la station.
    L = Point(A.x - 0.051408, A.y)                  # Le point situé à gauche de la station.
    R = Point(A.x + 0.051408, A.y)                  # Le point situé à droite de la station.
    U = Point(A.x, A.y + 0.01799425)                # Le point situé en haut de la station.
    D = Point(A.x, A.y - 0.01799431)                # Le point situé en bas de la station.
    UL = Point(L.x,U.y)
    DL = Point(L.x,D.y)
    UR = Point(R.x,U.y)
    DR = Point(R.x,D.y)
    # print("\n \n \n \n \n \n pos_centroids : ", pos_centroids, "\n \n \n \n \n \n ")
    # filtre les données du DataFrame pos_centroids pour récupérer les centroides qui se trouvent à gauche et à droite de la station, en fonction de leurs coordonnées :
    centroids_left = pos_centroids.iloc[np.where((pos_centroids.longitude > L.x) & (pos_centroids.longitude < A.x) & (pos_centroids.latitude < U.y) & (pos_centroids.latitude > D.y))]
    # print("\n \n \n \n \n \n Centroids_left : ", centroids_left)
    centroids_right = pos_centroids.iloc[np.where((pos_centroids.longitude < R.x) & (pos_centroids.longitude > A.x) & (pos_centroids.latitude < U.y) & (pos_centroids.latitude > D.y))]
    # print("Centroids_right : ", centroids_right, "\n \n \n \n \n \n ")
    if show == True:
        fig, ax = plt.subplots()
        ax.scatter([L.x,R.x,U.x,D.x,UL.x,DL.x,UR.x,DR.x], [L.y,R.y,U.y,D.y,UL.y,DL.y,UR.y,DR.y])
        ax.annotate('L', (L.x,L.y))
        ax.annotate('R', (R.x,R.y))
        ax.annotate('U', (U.x,U.y))
        ax.annotate('D', (D.x,D.y))
        ax.annotate('UL', (UL.x,UL.y))
        ax.annotate('DL', (DL.x,DL.y))
        ax.annotate('UR', (UR.x,UR.y))
        ax.annotate('DR', (DR.x,DR.y))
        ax.scatter([centroids_left.longitude.iloc[i] for i in range(len(centroids_left))], [centroids_left.latitude.iloc[i] for i in range(len(centroids_left))])
        ax.scatter([centroids_right.longitude.iloc[i] for i in range(len(centroids_right))], [centroids_right.latitude.iloc[i] for i in range(len(centroids_right))])
        ax.scatter(A.x, A.y)
        ax.annotate("'{}'".format(id_station), (A.x - 0.003, A.y-0.003))
        ax.legend(loc = (1.01,0.78), labels = ('limites','centroides à gauche','centroides à droite'))
        ax.set_title("Station '{}'.format(id_station", fontsize = 14)
        print("Distances avec la station '{}' :".format(id_station))
        [print(j,Geod.Inverse(A.y,A.x,i.y,i.x)['s12']) for i,j in zip([L,R,U,D,UL,DL,UR,DR],['L','R','U','D','UL','DL','UR','DR'])]
        print('\n')
    return centroids_left, centroids_right

# fonction to find the best drt stop
def find_best_drt_stop(stations):
    station0=pd.DataFrame()
    inacc_totals=[]

    for station in stations:
        centroids_left, _ =choose(station,False)
        # print("centroid_left: ",centroids_left)

        inacc_total=res[res["centroid"].isin(centroids_left["centroid_id"])]["inaccessibilite"].sum()
        inacc_totals.append(inacc_total)
        
        # print("inaccessibilite: ",inacc_total)

     
    station0["stop_id"]=stations
    station0["inacc_total"]=inacc_totals

    print(station0.sort_values("inacc_total",ascending=False))

    max_index = station0['inacc_total'].idxmax()
    chosen_stop_id_value = station0.loc[max_index, 'stop_id']

    return chosen_stop_id_value



################################################################

# variables
h = Parameters.h
longueur = Parameters.longueur  # longitude
largeur = Parameters.largeur    # latitude 
Data = Parameters.Data
nb_drt=Parameters.nb_DRT # number of station drt

#path to neccesary  data files
path_res = os.path.normpath('Results_{}/res/res_{}_min_0DRT.txt'.format(Data, int(h/60)))
path_stops = os.path.normpath('{}/stops.txt'.format(Data))
path_distances = os.path.normpath('{}/distances.txt'.format(Data))
path_pos_centroids = os.path.join(Data,"pos_centroids.txt")


res = pd.read_csv(path_res)
stops = pd.read_csv(path_stops)
distances = pd.read_csv(path_distances)
pos_centroids=pd.read_csv(path_pos_centroids)

stations = get_stations_df()
# print('stations : \n', stations.head())

#merge with lon/lat and sort all centroid with increasing accessibility 
res = res.merge(pos_centroids, left_on='centroid', right_on="centroid_id")
res = res.sort_values('accessibilite')

# print(res)

nb_drt=1


#loop by the number of drt stations
for i in range(nb_drt):
    print("lowest_acc_centroid:")
    print(res.head(10)[["centroid","inaccessibilite","accessibilite"]])


    
    # lowest_acc_centroid_id=res.head(1)["centroid"]
    min_index = res['accessibilite'].idxmin()
    lowest_acc_centroid_id = res.loc[min_index, 'centroid']

    print("\n\n\ncentroid id : ", lowest_acc_centroid_id)

    #position of centroid with lowest accesibility
    x=res.head(1)["longitude"]
    y=res.head(1)["latitude"]

    # print(x)
    # print(y)

    #need to generalize en term of drt zone size
    A = Point(x,y)                                  # Les coordonnées du centroid
    L = Point(A.x - 0.051408, A.y)                  # Le point situé à gauche du centroid.  0.051408=4km
    R = Point(A.x + 0.051408, A.y)                  # Le point situé à droite du centroid.
    U = Point(A.x, A.y + 0.01799425)                # Le point situé en haut du centroid.   0.01799425=1km
    D = Point(A.x, A.y - 0.01799431)                # Le point situé en bas du centroid.
    UL = Point(L.x,U.y)
    DL = Point(L.x,D.y)
    UR = Point(R.x,U.y)
    DR = Point(R.x,D.y)

    #case where we consider stop drt is always at the middle of right edge of the drt zone 
    possible_stops = stops.iloc[np.where((stops.stop_lon <= R.x) & (stops.stop_lon >= A.x) & (stops.stop_lat <= U.y) & (stops.stop_lat >= D.y))]["stop_id"].tolist()
    
    print("possible DRT stops: " ,possible_stops)

    #find the best station among the possible stations
    chosen_drt=find_best_drt_stop(possible_stops)
    print("The best DRT stop:",chosen_drt)

    #exclude all the centroids that are already included that drt zone 
    centroids_id=choose(chosen_drt,False)
    

    # res= 

    
    #wrtie that stop to a file
    




