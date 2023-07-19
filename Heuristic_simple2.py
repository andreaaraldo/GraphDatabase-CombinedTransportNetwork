import pandas as pd
import matplotlib as matplotlib
import os
import Parameters
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point
from geographiclib.geodesic import Geodesic
import sys
import subprocess


'''
nb_centr est la taille de couple_min_max_zoneDRT (nombre de zones que l'on a à chaque instant)
Commencer à nb_centr=30 pour Royan (dans Heuristic_iter.py)
'''

# Le nombre de centroides sur lesquels on va travailler : parmis les nb_centr centroides les moins accessibles, quels sont ceux sur lesquels il y aura un DRT
# Récupérer les arguments de la ligne de commande
nb_centr_init = int(sys.argv[1])
nb_DRT = int(sys.argv[2])
#print("nb_DRT : ", nb_DRT)
show_fig = False

# variables
h = Parameters.h
longueur = Parameters.longueur_degres      # de degré -> longitude 
largeur = Parameters.largeur_degres        # de degré -> latitude 
Data = Parameters.Data

###################################################
# Fonctions 
###################################################
# pour créer le répertoire des résultats ()
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

def afficher_centroide(): #larg et long les paramètres du rectangle 
    centroid_lon = res_acc['centroid_lon']
    centroid_lat = res_acc['centroid_lat']
    
    # Affichage du centroide
    #ax.plot(centroid_lon, centroid_lat, c = res_acc['accessibilite'], alpha = 0.3, label='Centroides')
    plt.plot(centroid_lon, centroid_lat, 'bo', alpha = 0.1, label='Centroides')

def afficher_stops():
    geod = Geodesic.WGS84
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
    plt.plot(*Ville.exterior.xy)        # trace le contour de la ville
    plt.title("{} zones de DRT possibles \n Largeur de la ville : {:.3g} km    |    Longueur de la ville : {:.3g} km".format(nb_centr, large, longu))

def afficher_centroids():
    # Coordonnées des centroids
    centroid_lon = centroids.centroid_lon
    centroid_lat = centroids.centroid_lat
    plt.scatter(centroid_lon, centroid_lat, alpha = 0.5)
    # Tracer les rectangles autour des centroids
    for lon, lat in zip(centroid_lon, centroid_lat):
        haut = lat + largeur/2
        bas = lat - largeur/2
        gauche = lon - longueur
        droite = lon
        x = [gauche, droite, gauche, droite]
        y = [haut, haut, bas, bas]
        plt.plot(x,y, '+')

# dataframe : couple_min_max_zoneDRT
def afficher_zone_DRT(dataframe): 
    nb_zones = dataframe.shape[0]
    for i in range(nb_zones):
        centr_lon = dataframe['lon_min'].iloc[i]
        centr_lat = dataframe['lat_min'].iloc[i]
        #le stop est au centre de la largeur droite
        # donc on recherche un stop à droite du centroide.
        bord_gauche = centr_lon                 # range_lon_min
        bord_droite = centr_lon + longueur      # range_lon_max
        # au centre du côté droit
        bord_bas = centr_lat - largeur/2          # range_lat_min
        bord_haut = centr_lat + largeur/2         # range_lat_max

        x = [bord_gauche,bord_gauche, bord_droite, bord_droite, bord_gauche] #on en met 5 pour refermer le rectangle
        y = [bord_haut, bord_bas, bord_bas, bord_haut, bord_haut]
        
        plt.plot(x, y, alpha = 0.7)
        #plt.plot(centr_lon,centr_lat, c='red')

# cette fonction renvoie les stops autour du n-ème centroid du tableau couple_min_max_zoneDRT
def exist_stop_autour(couple_min_max_zoneDRT, n):
    centr_lon = couple_min_max_zoneDRT['lon_min'].iloc[n]
    centr_lat = couple_min_max_zoneDRT['lat_min'].iloc[n]

    bord_gauche = centr_lon                 # range_lon_min
    bord_droite = centr_lon + longueur      # range_lon_max
    bord_bas = centr_lat - largeur/2        # range_lat_min
    bord_haut = centr_lat + largeur/2       # range_lat_max
    
    #On cherche les stops autour du n-ème centroide (cette liste reste vide s'il n'y a pas de centroide autour)
    liste_stops_autour = []

    nb_stops = stops.shape[0]
    for i in range(nb_stops):
        lon = stops['stop_lon'].iloc[i]
        lat = stops['stop_lat'].iloc[i]
        if bord_gauche <= lon <= bord_droite and bord_bas <= lat <= bord_haut: 
            liste_stops_autour.append(stops['stop_id'].iloc[i])
    return liste_stops_autour

def afficher_carte_complete(show_centroid, show_stops, show_zoneDRT, dataframe, titre, show):
    if show_centroid == True:
        afficher_centroide()
    if show_stops == True:
        afficher_stops()
    if show_zoneDRT == True:
        afficher_zone_DRT(dataframe)
    plt.xlabel('longitude')
    plt.ylabel('latitude')
    large, longu = calcul_taille_ville()
    #plt.title("{} zones possibles | {} DRT  \nLargeur de la ville : {:.3g} km |  Longueur : {:.3g} km \n {} ".format(nb_centr, nb_DRT, large, longu, titre))
    plt.title("{} zones possibles | {} DRT  \n {} ".format(nb_centr, nb_DRT, titre))
    if show == True :
        plt.show()

def calcul_taille_ville():
    geod = Geodesic.WGS84
    min_lat = min(stops.stop_lat) # Coordonnées limites des stops
    max_lat = max(stops.stop_lat)
    min_lon = min(stops.stop_lon)
    max_lon = max(stops.stop_lon)
    point_up_left = Point(min_lon, max_lat) # Points geometriques des limites
    point_up_right = Point(max_lon, max_lat)
    point_down_left = Point(min_lon, min_lat)

    # Calcule la largeur et la longueur de la ville
    larg = geod.Inverse(point_up_left.y, point_up_left.x, point_up_right.y, point_up_right.x)
    large = larg['s12']/1000 # largeur en km
    long = geod.Inverse(point_up_left.y, point_up_left.x, point_down_left.y, point_down_left.x)
    longu = long['s12']/1000 # Longueur en km
    return large, longu
    
def update_nb_centr_init(value):
    with open('nb_centr_init.txt', 'w') as file:
        file.write(str(value))
###################################################
# Heuristique simple 2
####################################################

#on crée le dossier (s'il n'existe pas encore) qui recense les meilleurs emplacements pour mettre les DRT (suivant l'heuristique) 

dir_path = os.path.normpath('./Results_{}/Placement_DRT'.format(Data))
filename = os.path.join(dir_path, 'DRT_placement_stops.txt')

create_result_file(filename)

#On récupère les résultats calculés (PCC) dans un dataframe
path_res = os.path.normpath('Results_{}/res/res_{}_min_0DRT.txt'.format(Data, int(h/60)))
res = pd.read_csv(path_res)
#print('Dataframe res : \n', res.head())
#print('res.shape[0] : \n', res.shape[0])

# On associe les accessibilités calculées aux stops :
path_centroids = os.path.normpath('{}/centroids.txt'.format(Data))
centroids = pd.read_csv(path_centroids)
centroids = centroids.drop_duplicates(subset='centroid_id')
centroids = centroids[['centroid_id','centroid_lon','centroid_lat']].copy()     # On ne garde que les colonnes utiles
centroid_id = centroids['centroid_id'].tolist()
#print("centroids : \n ", centroids.head())

# On associe les accessibilités calculées aux stops :
path_stops = os.path.normpath('{}/stops.txt'.format(Data))
stops = pd.read_csv(path_stops)
stop_id = stops['stop_id'].tolist()

#print(stops.head(0))

# On crée un dataframe res_acc qui a seulement les colonnes : 'centroid', 'accessibilite', 'centroid_lat', 'centroid_lon'
# On fusionne les dataframe res et centroids afin d'avoir dans le même dataframe l'accessibilité et les coordonnées
res_acc = res[['centroid', 'accessibilite']].copy()
#print("res acc \n ", res_acc, "\n \n ")
res_acc = res_acc.merge(centroids, left_on='centroid', right_on='centroid_id')

#print("res merged \n ", res_acc, "\n \n ")
res_acc = res_acc.sort_values('accessibilite')          # On trie le tableau par ordre croissant d'accessibilité

nb_centr = nb_centr_init    
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

stop = None
lon_stop = None
lat_stop = None
acc_stop = None
diff = None

couple_min_max_zoneDRT = pd.DataFrame({
    'centroid_min': centroid_min,
    'lon_min': lon_min,
    'lat_min': lat_min,
    'acc_min': acc_min,
    'stops_autour': stops_autour,
    'stop': stop,
    'lon_max': lon_stop,
    'lat_max': lat_stop,
    'acc_max': acc_stop,
    'diff': diff
})

#print("taille couple_min_max_zoneDRT : ", couple_min_max_zoneDRT.shape[0], "\n  couple_min_max_zoneDRT : \n", couple_min_max_zoneDRT.head())
##############################################################################################################################

#on parcourt la liste des centroids les plus exentrés (stops dont l'accessibilité est la plus faible)
# rappel : nb_centr est la taille du dataframe res (le nombre de centroides pour lesquels on cherche des stops autour)

stops_autour = []   # liste de listes
liste_stops = []    # composée de toutes les valeurs de stops_autour (mais sans sous liste)
for n in range(nb_centr) :
    liste_stops_autour = exist_stop_autour(couple_min_max_zoneDRT, n)   #renvoie la liste des stops autour du centroide
    for i in range(len(liste_stops_autour)): liste_stops.append(liste_stops_autour[i])
    stops_autour.append(liste_stops_autour)
couple_min_max_zoneDRT['stops_autour'] = stops_autour
    
#print("couple_min_max_zoneDRT : \n", couple_min_max_zoneDRT.head(15), "\n \n \n")

# on affiche les nb_centr zones de DRT possibles 
afficher_carte_complete(show_centroid=True, show_stops=True, show_zoneDRT=True, dataframe=couple_min_max_zoneDRT, titre = '', show = show_fig)


########################################################################################
# On trie le Dataframe couple_min_max_zoneDRT pour ne garde que les stops pertinents 
########################################################################################

# 1 - On supprime les centroides qui n'ont pas de stop autour :
couple_min_max_zoneDRT = couple_min_max_zoneDRT[couple_min_max_zoneDRT['stops_autour'].apply(lambda x: x != [])]

# on affiche les nb_centr zones de DRT possibles 
afficher_carte_complete(show_centroid=True, show_stops=True, show_zoneDRT=True, dataframe=couple_min_max_zoneDRT, titre = 'Après avoir enlevé les zones sans stops', show = show_fig)
########################################################################################

# Le nouveau dataframe :
#print("couple_min_max_zoneDRT sans les centroids isolés (qui n'ont pas de stop autour d'eux) : \n", couple_min_max_zoneDRT.head())

def remplir_stop_colonne(couple_min_max_zoneDRT):
    nb_centr = couple_min_max_zoneDRT.shape[0]  #le nb de lignes dans le tableau
    for i in range(nb_centr):
        liste_stops_autour = couple_min_max_zoneDRT['stops_autour'].iloc[i]
        if len(liste_stops_autour)==0:
            couple_min_max_zoneDRT = couple_min_max_zoneDRT.drop(i)
        elif len(liste_stops_autour)==1:  #on prend le seul stop dans le périmètre
            couple_min_max_zoneDRT['stop'].iloc[i] = liste_stops_autour[0]
            #couple_min_max_zoneDRT.loc[i, 'stop'] = liste_stops_autour[0]
        else : #mettre un autre critère : pour l'instant, on prend le premier (aléatoire)
            # critère : il ne faut pas que les zones se recoupent 
            # 
            couple_min_max_zoneDRT['stop'].iloc[i] = liste_stops_autour[0]
            #couple_min_max_zoneDRT.loc[i, 'stop'] = liste_stops_autour[0]
    return couple_min_max_zoneDRT

# 2 - On supprime les zones qui sont rattachées au même stop : on conserve la zone dans laquelle il y a l'accessibilité minimale pour un même stop.
def supprimer_zones_meme_stop(couple_min_max_zoneDRT):
    # Utiliser groupby pour regrouper les lignes par identifiant "stop" et obtenir l'index de la ligne avec la valeur minimale de "acc_min"
    index_min_accessibilite = couple_min_max_zoneDRT.groupby('stop')['acc_min'].idxmin()
    # Sélectionner les lignes correspondant aux index obtenus
    couple_min_max_zoneDRT = couple_min_max_zoneDRT.loc[index_min_accessibilite]
    return couple_min_max_zoneDRT

couple_min_max_zoneDRT = remplir_stop_colonne(couple_min_max_zoneDRT)
couple_min_max_zoneDRT = supprimer_zones_meme_stop(couple_min_max_zoneDRT)

#print("couple_min_max_zoneDRT sans répétition de stop \n",couple_min_max_zoneDRT.head())
# on affiche les nb_centr zones de DRT possibles 
afficher_carte_complete(show_centroid=True, show_stops=True, show_zoneDRT=True, dataframe=couple_min_max_zoneDRT, titre = 'Après avoir enlevé les zones sur les mêmes stops', show = show_fig)

'''
# 3 - On ne garde que les stops suffisamment éloignés les uns des autres 
def stops_eloignes(liste_stops, couple_min_max_zoneDRT):
    # Liste filtrée des stops éloignés
    liste_stops_filtree = []
    # Parcours des stops
    for i in range(len(liste_stops)):
        stop = liste_stops[i]
        latitude = stops.loc[stops['stop_id'] == stop, 'stop_lat'].values[0]
        longitude = stops.loc[stops['stop_id'] == stop, 'stop_lon'].values[0]

        # Vérification de la distance par rapport aux stops précédents
        is_sufficiently_separated = True
        for j in range(i):
            previous_stop = liste_stops[j]
            previous_latitude = stops.loc[
                stops['stop_id'] == previous_stop, 'stop_lat'].values[0]
            previous_longitude = stops.loc[
                stops['stop_id'] == previous_stop, 'stop_lon'].values[0]

            # Vérification de la distance en latitude et longitude
            if abs(latitude - previous_latitude) < largeur or abs(longitude - previous_longitude) < longueur:
                is_sufficiently_separated = False
                break

        if is_sufficiently_separated:
            liste_stops_filtree.append(stop)

    nb_centr = couple_min_max_zoneDRT.shape[0]
    i = 0
    while i < nb_centr:
        l = couple_min_max_zoneDRT['stops_autour'].iloc[i]
        l = [value for value in l if value in liste_stops_filtree]
        #couple_min_max_zoneDRT.loc[i, 'stops_autour'] = l
        if len(l) == 0 : 
            couple_min_max_zoneDRT = couple_min_max_zoneDRT.drop(couple_min_max_zoneDRT.index[i])
        else : 
            couple_min_max_zoneDRT.at[i, 'stops_autour'] = l
            i = i+1
    # Affichage des stops filtrés
    return couple_min_max_zoneDRT

couple_min_max_zoneDRT = stops_eloignes(liste_stops, couple_min_max_zoneDRT)

# 3.b - On supprime les centroides qui n'ont pas de stop autour :
couple_min_max_zoneDRT = couple_min_max_zoneDRT[couple_min_max_zoneDRT['stops_autour'].apply(lambda x: x != [])]

# on affiche les nb_centr zones de DRT possibles 
afficher_carte_complete(show_centroid=True, show_stops=True, show_zoneDRT=True, dataframe=couple_min_max_zoneDRT, titre = 'Après avoir enlevé les zones qui se recoupaient', show = show_fig)
'''

# Parmis ces Emplacements, on choisit les nb_DRT meilleurs emplacements 
nb_centr = couple_min_max_zoneDRT.shape[0]
'''
if nb_centr == nb_DRT :
    # on prend tous les stops trouvés
    placement_DRT = couple_min_max_zoneDRT['stop'].tolist() 
    # Mettre ces résultats dans le fichier à la ligne n° nb_DRT
    ecrire_ligne(filename, nb_DRT, placement_DRT)
'''
if nb_centr >= nb_DRT :
    # on choisit nb_DRT parmis les stops 
    placement_DRT = couple_min_max_zoneDRT['stop'].tolist() 
    placement_DRT = placement_DRT[:nb_DRT]
    # Mettre ces résultats dans le fichier à la ligne n° nb_DRT
    ecrire_ligne(filename, nb_DRT, placement_DRT)
    # Écrire la valeur mise à jour de nb_centr_init dans le fichier
    update_nb_centr_init(nb_centr_init)
elif nb_centr < nb_DRT :
    nb_centr_init += (nb_DRT-nb_centr)*10    #si la différence est grande, on augmente fortement le nombre de centroides
    nb_centr_total = centroids.shape[0]
    if nb_centr_init > nb_centr_total : nb_centr_init = nb_centr_total  #On ne peux pas dépasser nb_centr_total
    # on augmente nb_centr du début
    print('nb_centr : ', nb_centr)
    print('nb_DRT : ', nb_DRT)
    print('nb_centr_init : ', nb_centr_init)
    subprocess.run(['python3', 'Heuristic_simple2.py',str(nb_centr_init), str(nb_DRT)])

#####################################################################################
# Placer les zones de DRT avec les stops choisis sur le plus petit côté (largeur)
#####################################################################################


#################################################################################
