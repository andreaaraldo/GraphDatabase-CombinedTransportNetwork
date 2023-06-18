import pandas as pd
import matplotlib as matplotlib
import os
import sys
import Parameters
from sklearn.neighbors import NearestNeighbors

'''
Il faudrait avec une zone de taille $**longueur** x **largeur**$ (paramètres définis dans Parameters) dans laquelle 
il y a à la fois des accessibilités faibles (mauvaise desserte) et des accessibilités fortes.
Ou les mettre autour d'endroits où il y a des correspondances.
'''

# variables
h = Parameters.h
longueur = Parameters.longueur  # longitude
largeur = Parameters.largeur    # latitude 

# Vérifier le nombre d'arguments passés
if len(sys.argv) != 2:
    print("Usage: python3 Heuristic_simple2.py nombre_DRT")
    sys.exit(1)

# Récupérer les variables
nb_DRT = int(sys.argv[1])


# cette fonction servira à écrire dans le document qui recense les emplacements des DRTs
def ecrire_ligne(nom_fichier, ligne, contenu):
    # Ouvrir le fichier en mode ajout
    with open(nom_fichier, "r+") as fichier:
        lignes = fichier.readlines()

        # Vérifier si la ligne spécifiée est valide
        if ligne < 0 :
            print("Ligne invalide.")
            return
        #elif ligne_m >= len(lignes):
        # Déplacer le curseur au début de la ligne spécifiée
        fichier.seek(0)
        for i, l in enumerate(lignes):
            if i == ligne:
                # Écrire le contenu dans la ligne spécifiée
                fichier.write(str(contenu) + "\n")
            else:
                fichier.write(l)

    print("Écriture terminée dans le fichier ", nom_fichier)

###################################################
# Heuristique simple 2
####################################################

#on crée le dossier (s'il n'existe pas encore) qui recense les meilleurs emplacements pour mettre les DRT (suivant l'heuristique) 

filename = os.path.normpath('./Heuristic/DRT_heuristique_simple2.txt')

if not os.path.exists(filename):
    # Create the file if it doesn't exist
    with open(filename, "x") as file:
        # Write 30 blank lines
        for _ in range(30):
            file.write("\n")
    print(filename, " created.")
else:
    print(filename, " already exists.")

#Création d'un dataframe avec les résultats calculés
path_res = os.path.normpath('Results/res/res_{}_min_0DRT.txt'.format(int(h/60)))
res = pd.read_csv(path_res)
#print(res.head())

# On associe les accessibilités calculées aux stops :
path_stops = os.path.normpath('{}/stops.txt'.format(Data))
stops = pd.read_csv(path_stops)

print(stops.head(0))

# Obtenir les identifiants des stops
stop_id = stops['stop_id'].tolist()

# Filtrer les lignes du dataframe res en fonction des identifiants des stops
res_stops = res[res['centroid'].isin(stop_id)]

print("res_stops", res_stops.head(0))


# Fusionner data_centroids_drop avec res_1_min sur la colonne 'centroid_id' pour avoir les coordonnées et les inaccessibilités
res_stops_merge = stops.merge(res_stops, left_on='stop_id', right_on='centroid')

res_stops_merge.drop(["stop_code", "stop_name", "stop_desc", "nb_destinations", "centroid", "trajets", "trajets_ok", "nb_station_DRT", "DRT", "DRT_ok", "WALK_to_station_DRT", "WALK"], axis=1, inplace=True)
#print(res_stops_merge.head(0))
#print(res_stops_merge.head())


# Trier le DataFrame par ordre croissant en fonction de la colonne accessibilite
res_stops_sorted = res_stops_merge.sort_values('accessibilite')
print('dataframe trié : ', res_stops_sorted.head())

# Extraire les m premières lignes du DataFrame trié --> les moins accessibles
res_min_acc = res_stops_sorted.head(30)
# Extraire les m dernières lignes du DataFrame trié --> les plus accessibles
res_max_acc = res_stops_sorted.tail(nb_DRT)

###############################################################
# On crée le dataframe dans lequel on mettra les informations 


stop_min = res_min_acc['stop_id'].tolist()
taille_df = len(stop_min)

lon_min = res_min_acc['stop_lon'].tolist()
lat_min = res_min_acc['stop_lat'].tolist()
acc_min = res_min_acc['accessibilite'].tolist()

stop_max = [0]*taille_df
lon_max = [0]*taille_df
lat_max = [0]*taille_df
acc_max = [0]*taille_df
diff = [0]*taille_df

couple_min_max_zoneDRT = pd.DataFrame({
    'stop_min': stop_min,
    'lon_min': lon_min,
    'lat_min': lat_min,
    'acc_min': acc_min,
    'stop_max': stop_max,
    'lon_max': lon_max,
    'lat_max': lat_max,
    'acc_max': acc_max,
    'diff': diff
})


#on parcourt la liste des centroids les plus exentrés (stops dont l'accessibilité est la plus faible)
#Pour cela, on parcourt les lignes du dataframe couple_min_max_zoneDRT pour associer à chaque stop_min un stop_max
for n in range(taille_df) :
    range_lon_min = couple_min_max_zoneDRT['lon_min'].iloc[n] - longueur
    range_lon_max = couple_min_max_zoneDRT['lon_min'].iloc[n] + longueur
    range_lat_min = couple_min_max_zoneDRT['lat_min'].iloc[n] - largeur
    range_lat_max = couple_min_max_zoneDRT['lat_min'].iloc[n] + largeur
    print("[range_lon_min, range_lon_min]", range_lon_min, range_lon_min)
    #On cherche le stops dont l'accessibilité est la plus élevée autour de ce stop là
    #On regarde tous les stops qui se trouvent dans le range autour de stop_min :
    stops_autour = []
    acc_stops_autour = []
    latitude = []
    longitude = []
    for i in range(res_stops_merge.shape[0]):
        lon = res_stops_merge['stop_lon'].iloc[i]
        lat = res_stops_merge['stop_lat'].iloc[i]
        if range_lon_min <= lon <= range_lon_max and range_lat_min <= lat <= range_lat_max: 
            stops_autour.append(res_stops_merge['stop_id'].iloc[i])
            acc_stops_autour.append(res_stops_merge['accessibilite'].iloc[i])
            longitude.append(lon)
            latitude.append(lat)
        id_acc_max = acc_stops_autour.index(max(acc_stops_autour))
    couple_min_max_zoneDRT.loc[n, 'stop_max'] = stops_autour[id_acc_max]
    couple_min_max_zoneDRT.loc[n, 'acc_max']= acc_stops_autour[id_acc_max]
    couple_min_max_zoneDRT.loc[n, 'lon_max'] = longitude[id_acc_max]
    couple_min_max_zoneDRT.loc[n, 'lat_max'] = latitude[id_acc_max]
    couple_min_max_zoneDRT.loc[n, 'diff'] = couple_min_max_zoneDRT['acc_max'].iloc[n] - couple_min_max_zoneDRT['acc_min'].iloc[n]

print("couple_min_max_zoneDRT : ", couple_min_max_zoneDRT.head())


#On trie le dataframe selon la différence d'accessibilité : 
couple_min_max_zoneDRT_sorted = couple_min_max_zoneDRT.sort_values('diff')
print('couple_min_max_zoneDRT trié : ', couple_min_max_zoneDRT_sorted.head())

#On garde les premières lignes du tableau (là où l'on va placer les DRT)
couple_min_max_zoneDRT_choix_DRT = couple_min_max_zoneDRT_sorted.head(nb_DRT)

#placement DRT sans recadrage
placement_DRT = []

#placement DRT avec recadrage 
for i in range(nb_DRT):
    centre_lon = (couple_min_max_zoneDRT_choix_DRT['lon_max'].iloc[i] + couple_min_max_zoneDRT_choix_DRT['lon_min'].iloc[i])/2
    centre_lat = (couple_min_max_zoneDRT_choix_DRT['lat_max'].iloc[i] + couple_min_max_zoneDRT_choix_DRT['lat_min'].iloc[i])/2
    # Créer l'arbre k-d avec les points existants
    # Créer un modèle de recherche des plus proches voisins
    k = 1  # Nombre de voisins à rechercher (1 dans ce cas pour le point le plus proche)
    nbrs = NearestNeighbors(n_neighbors=k, algorithm='auto').fit(couple_min_max_zoneDRT[['lon_min', 'lat_min']])

    # Rechercher le point le plus proche du nouveau point
    distances, indices = nbrs.kneighbors([[centre_lat, centre_lon]])
    index = indices.flatten()[0]
    # Obtenir la valeur de stop_min du point le plus proche
    stop_centre_id = couple_min_max_zoneDRT_sorted.loc[index, 'stop_min']

    print("Valeur de stop_min du point le plus proche :", stop_centre_id)
    placement_DRT.append(stop_centre_id)

#################################################################################
# Mettre ces résultats dans le fichier à la ligne n° nb_DRT
ecrire_ligne(filename, nb_DRT, placement_DRT)