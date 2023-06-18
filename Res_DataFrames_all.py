import pandas as pd
import numpy as np
import os
import Parameters
import time

Data = Parameters.Data

def get_nb_DRT(df_centroid):
    j = 0
    for i in df_centroid.transport:
        if (i == 'DRT/WALK') or (i == 'DRT'):
            j += 1
    return j

def get_traj_rais(df_centroid):
    j = 0
    for i in np.where(df_centroid.total_time != 'None')[0]:
        if float(df_centroid.iloc[i].total_time) < df_centroid.iloc[i].direct_walk_time:
            j += 1
    return j

def get_traj_rais_DRT(df_centroid):
    j = 0
    for i in np.where(df_centroid.total_time != 'None')[0]:
        if (float(df_centroid.iloc[i].total_time) < float(df_centroid.iloc[i].direct_walk_time)) & ((df_centroid.iloc[i].transport == 'DRT') or (df_centroid.iloc[i].transport == 'DRT/WALK')):
            j += 1
    return j

def get_total_times(df_centroid):
    times = []
    for i in np.where(df_centroid.total_time != 'None')[0]:
        times.append(min(float(df_centroid.iloc[i].total_time), float(
            df_centroid.iloc[i].direct_walk_time)))
    for i in np.where(df_centroid.total_time == 'None')[0]:
        times.append(df_centroid.iloc[i].direct_walk_time)
    return times

def get_nb_station_DRT(df_centroid):
    j = 0
    for i in df_centroid['1st_station'].iloc[np.where(df_centroid.transport == 'DRT')]:
        if int(i) in stations:
            j += 1
    for i in df_centroid['1st_station'].iloc[np.where(df_centroid.transport == "DRT/WALK")]:
        if int(i) in stations:
            j += 1
    return j

def get_walk_to_drt(drt, station_drt):
    walk_to_drt = []
    for i in range(len(drt)):
        if (drt[i] == 'None') and (station_drt[i] == 'None'):
            walk_to_drt.append('None')
        else:
            walk_to_drt.append(station_drt[i]-drt[i])
    return walk_to_drt

def df_res(centroid_ids):
    df = pd.DataFrame()
    centroid_id = []  # id des centroides pouvant prendre le DRT
    nb_destinations = []  # nombre de stations dans le rayon
    nb_trajets = []  # nombre de PCC = nombre de stations ayant un chemin
    # nombre de PCC raisonnables = temps total plus petit que temps de marche direct
    nb_trajets_ok = []
    nb_DRT = []  # nombre de PCC ayant pris le DRT plutôt que la marche
    nb_DRT_ok = []  # nombre de trajets raisonnables ayant utilisé le service DRT
    nb_WALK = []  # nombre de PCC ayant pris la marche plutôt que le DRT
    nb_stations_DRT = []
    somme = []  # somme des temps totaux des PCC
    accessibilite = []  # 1/somme des temps totaux des PCC
    for id_c in centroid_ids:
        path = os.path.normpath("./Results_{}/h_{}_all/centroid_{}.txt".format(Data, h_str, id_c))
        centroid = pd.read_csv(path)
        print("centroid : \n", centroid)
        if not centroid.empty : 
            if all(centroid.total_time == 'None'):
                print(id_c, 'vide')
                centroid_id.append(id_c)
                nb_destinations.append(len(centroid))
                nb_trajets.append('None')
                nb_trajets_ok.append('None')
                #print(centroid.head())
                total = 0
                for i in centroid.direct_walk_time:
                    total += i
                    #print les valeurs négatives
                    print(i)
                print("total = ", total)
                print("1/total = ", 1/total)
                #somme.append(sum([i for i in centroid.direct_walk_time]))
                accessibilite.append(1/total)
                somme.append(total)
                print("somme = ",somme)
                nb_DRT.append('None')
                nb_DRT_ok.append('None')
                nb_WALK.append('None')
                nb_stations_DRT.append('None')
            else:
                centroid_id.append(id_c)
                nb_destinations.append(len(centroid))
                nb_trajets.append(len([i for i in centroid.total_time if i != 'None']))
                nb_trajets_ok.append(get_traj_rais(centroid))
                somme.append(sum(get_total_times(centroid)))
                accessibilite.append(1/sum(get_total_times(centroid)))
                nb_DRT.append(get_nb_DRT(centroid))
                nb_DRT_ok.append(get_traj_rais_DRT(centroid))
                nb_WALK.append(len(np.where(centroid.transport == 'WALK')[0]))
                nb_stations_DRT.append(get_nb_station_DRT(centroid))
    df['centroid'] = centroid_id
    df['nb_destinations'] = nb_destinations
    df['trajets'] = nb_trajets
    df['trajets_ok'] = nb_trajets_ok
    df['nb_station_DRT'] = nb_stations_DRT
    df['DRT'] = nb_DRT
    df['DRT_ok'] = nb_DRT_ok
    df['WALK_to_station_DRT'] = get_walk_to_drt(nb_DRT, nb_stations_DRT)
    df['WALK'] = nb_WALK
    df['inaccessibilite'] = somme
    #df['somme_moyennée'] = [i/j for i, j in zip(somme, nb_destinations)]
    return df

################################################################################################################
start_time = time.time()

h_str = Parameters.h_str

res_path = os.path.normpath("./Results_{}/res".format(Data))


##Gestion de l'historique 
if not os.path.exists(res_path):
    # Crée le dossier 'res' s'il n'existe pas
    os.mkdir(res_path)

directory_res_all = "res_{}_all.txt".format(h_str)
dir_path = os.path.join("./Results_{}/res".format(Data), directory_res_all)
old_directory_res_all = "res_{}_old.txt".format(h_str)
old_dir_path = os.path.join("./Results_{}/res".format(Data), old_directory_res_all)

#Si le dossier res existe, alors on le renome _old et on supprime l'historique
if os.path.exists(dir_path):
    #on supprime l'historique s'il existe
    if os.path.exists(old_dir_path):
        os.remove(old_dir_path)
    #on renome le dossier pour le placer dans l'historique
    os.rename(dir_path, old_dir_path)

##Fin de gestion de l'historique 


path = os.path.normpath("./Results_{}/ids_all.txt".format(Data, h_str))

print("Creating centroid_ids...")
centroid_ids_all = [i for i in pd.read_csv(path)['centroid_id']]


stations = Parameters.liste_stations_DRT

print("Creating data...")
data = df_res(centroid_ids_all)
print("Done !")
path_res = os.path.normpath("./Results_{}/res/res_{}_all.txt".format(Data, h_str))
data.to_csv(path_res, index = False)

end_time = time.time()

print("temps d'exécution :", (end_time - start_time)/60, 'minutes')