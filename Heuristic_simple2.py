import pandas as pd
import matplotlib as matplotlib
import os
import Parameters
from sklearn.neighbors import NearestNeighbors
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from shapely.geometry import Polygon, LineString, Point
import geopandas as gpd
from geographiclib.geodesic import Geodesic

# variables
h = Parameters.h
longueur = Parameters.longueur  # longitude
largeur = Parameters.largeur    # latitude 
Data = Parameters.Data
nb_DRT = Parameters.nb_DRT

###################################################
# Fonctions utiles
###################################################
# pour créer le répertoire des résultats 
def create_result_file(filename):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    if not os.path.exists(filename):
        # Create the file if it doesn't exist
        with open(filename, "x") as file:
            # Write 30 blank lines
            for _ in range(30):
                file.write("\n")
        print(filename, " created.")
    else:
        print(filename, " already exists.")

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

def affichage_rectangle(larg, long): #larg et long les paramètres du rectangle 
    # Coordonnées des centroides
    centroid_latitudes = couple_min_max_zoneDRT['lat_min']
    centroid_longitudes = couple_min_max_zoneDRT['lon_min']
    print("centroid_latitudes", centroid_latitudes)

    # Création de la figure
    fig, ax = plt.subplots()

    # Affichage des centroides
    ax.scatter(centroid_longitudes, centroid_latitudes, color='blue', label='Centroides')

    # Affichage des rectangles
    for _, centroid in couple_min_max_zoneDRT.iterrows():
        rect = patches.Rectangle((centroid['lon_min'] - larg/2, centroid['lat_min'] - long/2), larg, long, linewidth=1, edgecolor='r', facecolor='none')
        ax.add_patch(rect)

    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.legend()

def affichage_rectangle(larg, long): #larg et long les paramètres du rectangle 
    # Création de la figure et des axes
    fig, ax = plt.subplots()

    # Affichage des centroides et des rectangles
    for _, centroid in centroids.iterrows():
        centroid_lon = centroid['centroid_lon']
        centroid_lat = centroid['centroid_lat']
        
        # Affichage du centroide
        ax.plot(centroid_lon, centroid_lat, 'bo', label='Centroide')
        
        # Création du rectangle autour du centroide
        rect = patches.Rectangle((centroid_lon - larg/2, centroid_lat - long/2), larg, long,
                                linewidth=1, edgecolor='r', facecolor='none')
        ax.add_patch(rect)

    # Configuration de l'axe des coordonnées
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')

    # Affichage de la légende
    ax.legend()

# Cree pavage (polygones)
def pavage():
    min_lat = min(stops.stop_lat) # Coordonnées limites des stops
    max_lat = max(stops.stop_lat)
    min_lon = min(stops.stop_lon)
    max_lon = max(stops.stop_lon)
    lon = (max_lon - min_lon)/int(np.floor(largeur))
    lat = (max_lat - min_lat)/int(np.floor(longueur))
    cols = int(np.floor(largeur))
    rows = int(np.floor(longueur))
    lat_down = min_lat
    lon_right = max_lon
    polygons = []
    for i in range(cols):
        lat_up = max_lat
        lon_left = min_lon + lon*i
        for j in range(rows):
            polygons.append(Polygon([(lon_left, lat_up), (lon_left + lon, lat_up), (lon_left + lon, lat_up - lat), (lon_left, lat_up - lat)])) 
            lat_up = lat_up - lat
    grid = gpd.GeoDataFrame({'geometry':polygons})
    for i in range(len(polygons)):
        plt.plot(*polygons[i].exterior.xy)
    plt.scatter(stops.stop_lon, stops.stop_lat)

    ## Centoids of polygons on Royan
    plt.scatter(stops.stop_lon, stops.stop_lat)
    plt.scatter([polygons[i].centroid.x for i in range(len(polygons))], [polygons[i].centroid.y for i in range(len(polygons))], marker = '.')

    # Enregistrer le graph
    path_save_fig = os.path.normpath("./Results_{}/Centroids.png".format(Data))
    plt.savefig(path_save_fig, format = 'png') 
    #plt.savefig(r"./Results/Stations.svg", format = 'svg') 
    return polygons

def afficher_stops():
    geod = Geodesic.WGS84
    path_stops = os.path.normpath('./{}/stops.txt'.format(Data))
    stops = pd.read_csv(path_stops) # stops = pd.read_csv(r'{}/stops.txt'.format(Data)) for mac and linux
    min_lat = min(stops.stop_lat) # Coordonnées limites des stops
    max_lat = max(stops.stop_lat)
    min_lon = min(stops.stop_lon)
    max_lon = max(stops.stop_lon)
    point_up_left = Point(min_lon, max_lat) # Points geometriques des limites
    point_up_right = Point(max_lon, max_lat)
    point_down_left = Point(min_lon, min_lat)
    point_down_right = Point(max_lon, min_lat)

    # Calcule la largeur et la longueur de la ville
    larg = geod.Inverse(point_up_left.y, point_up_left.x, point_up_right.y, point_up_right.x)
    large = larg['s12']/1000 # largeur en km
    long = geod.Inverse(point_up_left.y, point_up_left.x, point_down_left.y, point_down_left.x)
    longu = long['s12']/1000 # Longueur en km

    ### Ville & contours
    Ville = Polygon([point_up_left, point_up_right, point_down_right, point_down_left])
    plt.scatter(stops.stop_lon, stops.stop_lat)
    plt.plot(*Ville.exterior.xy)
    plt.title("Largeur de la ville : {} km \n Longueur de la ville : {} km".format(large, longu))

def afficher_centroids():
    geod = Geodesic.WGS84
    min_lat = min(centroids.centroid_lat) # Coordonnées limites des stops
    max_lat = max(centroids.centroid_lat)
    min_lon = min(centroids.centroid_lon)
    max_lon = max(centroids.centroid_lon)
    point_up_left = Point(min_lon, max_lat) # Points geometriques des limites
    point_up_right = Point(max_lon, max_lat)
    point_down_left = Point(min_lon, min_lat)
    point_down_right = Point(max_lon, min_lat)
    plt.scatter(centroids.centroid_lon, centroids.centroid_lat)

###################################################
# Heuristique simple 2
####################################################

#on crée le dossier (s'il n'existe pas encore) qui recense les meilleurs emplacements pour mettre les DRT (suivant l'heuristique) 

dir_path = os.path.normpath('./Results_{}/Placement_DRT'.format(Data))
filename = os.path.join(dir_path, 'DRT_heuristique_simple.txt')

create_result_file(filename)

#On récupère les résultats calculés (PCC) dans un dataframe
path_res = os.path.normpath('Results_{}/res/res_{}_min_0DRT.txt'.format(Data, int(h/60)))
res = pd.read_csv(path_res)
print('Dataframe res : \n', res.head())
print('res.shape[0] : \n', res.shape[0])

# On associe les accessibilités calculées aux stops :
path_centroids = os.path.normpath('{}/centroids.txt'.format(Data))
centroids = pd.read_csv(path_centroids)
centroids = centroids.drop_duplicates(subset='centroid_id')
centroids = centroids[['centroid_id','centroid_lon','centroid_lat']].copy()     # On ne garde que les colonnes utiles
centroid_id = centroids['centroid_id'].tolist()
## print(centroids.head(0))

# On associe les accessibilités calculées aux stops :
path_stops = os.path.normpath('{}/stops.txt'.format(Data))
stops = pd.read_csv(path_stops)
stop_id = stops['stop_id'].tolist()
#print(stops.head(0))

# On crée un dataframe res_acc qui a seulement les colonnes : 'centroid', 'accessibilite', 'centroid_lat', 'centroid_lon'
# On fusionne les dataframe res et centroids afin d'avoir dans le même dataframe l'accessibilité et les coordonnées
res_acc = res[['centroid', 'accessibilite']].copy()
print("res acc \n ", res_acc, "\n \n ")
res_acc = res_acc.merge(centroids, left_on='centroid', right_on='centroid_id')

print("res merged \n ", res_acc, "\n \n ")
res_acc = res_acc.sort_values('accessibilite')          # On trie le tableau par ordre croissant d'accessibilité

# Le nombre de centroides sur lesquels on va travailler : parmis les nb_centr centroides les moins accessibles, quels sont ceux sur lesquels il y aura un DRT
nb_centr = 15           
res_min_acc = res_acc.head(nb_centr)                           # On garde les nb_centr premières lignes du Df (les centroides dont les accessibilités sont les plus faibles)

##############################################################################################################################
# couple_min_max_zoneDRT
# On crée le dataframe dans lequel on mettra les informations 
##############################################################################################################################

centroid_min = res_min_acc['centroid'].tolist()

lon_min = res_min_acc['centroid_lon'].tolist()
lat_min = res_min_acc['centroid_lat'].tolist()
acc_min = res_min_acc['accessibilite'].tolist()

# colonnes à remplir au fur et à mesure 
stops_autour = None

stop_max = None
lon_max = None
lat_max = None
acc_max = None
diff = None

couple_min_max_zoneDRT = pd.DataFrame({
    'centroid_min': centroid_min,
    'lon_min': lon_min,
    'lat_min': lat_min,
    'acc_min': acc_min,
    'stops': stops_autour,
    'stop_max': stop_max,
    'lon_max': lon_max,
    'lat_max': lat_max,
    'acc_max': acc_max,
    'diff': diff
})

#print("taille couple_min_max_zoneDRT : ", couple_min_max_zoneDRT.shape[0], "\n  couple_min_max_zoneDRT : \n", couple_min_max_zoneDRT.head())
##############################################################################################################################

#on parcourt la liste des centroids les plus exentrés (stops dont l'accessibilité est la plus faible)
# rappel : nb_centr est la taille du dataframe res (le nombre de centroides pour lesquels on cherche des stops autour)

# cette fonction renvoie les stops autour du n-ème centroid du tableau couple_min_max_zoneDRT
def exist_stop_autour(n):
    centr_lon = couple_min_max_zoneDRT['lon_min'].iloc[n]
    centr_lat = couple_min_max_zoneDRT['lat_min'].iloc[n]
    # Conversion des kilomètres en degrés de latitude et longitude approximatifs
    lat_deg_per_km = 1 / 110.574  # Approximation basée sur la latitude moyenne
    lon_deg_per_km = 1 / (111.320 * math.cos(math.radians(centr_lat)))  # Approximation basée sur la latitude

    # On crée la zone autour du n-ème centroid dans laquelle on recherche des stops
    '''
    bord_gauche = centr_lat - longueur * lat_deg_per_km     # range_lon_min
    bord_droite = centr_lat + longueur * lat_deg_per_km     # range_lon_max
    bord_bas = centr_lon - largeur * lon_deg_per_km         # range_lat_min
    bord_haut = centr_lon + largeur * lon_deg_per_km        # range_lat_max
    '''
    bord_gauche = centr_lon - longueur      # range_lon_min
    bord_droite = centr_lon + longueur      # range_lon_max
    bord_bas = centr_lat - largeur          # range_lat_min
    bord_haut = centr_lat + largeur         # range_lat_max

    x = [bord_gauche,bord_gauche, bord_droite, bord_droite]
    y = [bord_haut, bord_bas, bord_bas, bord_haut]
    labels = ['haut-gauche', 'bas-gauche','haut-droit', 'bas-droit']

    plt.scatter(x, y)
    plt.scatter(centr_lon,centr_lat, c='red')
    # Ajouter les labels aux points
    for i, label in enumerate(labels):
        plt.text(x[i], y[i], label, ha='center', va='bottom')
    plt.xlabel('longitude')
    plt.ylabel('latitude')
    #On cherche les stops autour du n-ème centroide (cette liste reste vide s'il n'y a pas de centroide autour)
    liste_stops_autour = []

    nb_stops = stops.shape[0]
    for i in range(nb_stops):
        lon = stops['stop_lon'].iloc[i]
        lat = stops['stop_lat'].iloc[i]
        if bord_gauche <= lon <= bord_droite and bord_bas <= lat <= bord_haut: 
            liste_stops_autour.append(stops['stop_id'].iloc[i])
    return liste_stops_autour

stops_autour = []
for n in range(nb_centr) :
    liste_stops_autour = exist_stop_autour(n)
    stops_autour.append(liste_stops_autour)

plt.show()

couple_min_max_zoneDRT['stops_autour'] = stops_autour
    
print("couple_min_max_zoneDRT : \n", couple_min_max_zoneDRT.head(15), "\n \n \n")


afficher_stops()
afficher_centroids()
plt.show()

'''
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

'''