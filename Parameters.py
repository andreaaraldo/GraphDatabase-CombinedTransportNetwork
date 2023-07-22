import os 
import numpy as np
import math

# Parametres

nb_DRT = 20
# indiquer les données qu'on utilise 
Data = "Data"
# Data = "small_instance"
# Data = "small_instance_scaled"
'''
Small instance :
largeur : 5,06km
longueur : 3,45km
'''

## Intervenant dans le fichier 'Reduce_Centroid_Stop.py' :
rayon_exclusif = 6500 # supprime les centroides n'ayant aucune station situee dans ce rayon. In meters
rayon_walk = 1000 # cree une relation WALK entre un centroide et les stations situees dans ce rayon. In meters
departure_time = "'08:30:00'" # horaire de depart pour tous les centroides
vitesse_walk = 3 # en km/h, vitesse moyenne de marche

## Intervenant dans le fichier 'Change_departure_time_centroid.py' :
new_departure_time = "'08:30:00'" # type String, nouvel horaire de départ pour tous les centroïdes

## Intervenant dans le fichier 'Load_DRT.py' :
h0 = [60, 120, 240, 960, 1920, 3840] # valeurs de h possibles (proposées). In seconds
idx_h = 0 # intervient également dans le fichier 'Res_DataFrames.py' plus bas
h = h0[idx_h] # valeur de h actuelle

densite = 26 # 26 pax/h/km^2, nombre de passagers par km² par heure

########################################################################
# Zones de DRT
########################################################################
# On cherche la latitude de la ville (pas besoin de précision) pour pouvoir convertir des km en mesure latitude/longitude
centroids_txt = os.path.normpath('{}/centroids.txt'.format(Data))
with open(centroids_txt, 'r') as file:
    content = file.readlines()
    first_line = content[1]
    columns = first_line.split(',')     # Diviser la ligne en colonnes
    lat = float(columns[2])    # Accéder à la valeur de centroid_lat (indice 2)


longueur = 4000 # en metres, longueur de la zone de service DRT (rectangulaire)
largeur = 2000 # en metres, largeur de la zone de service DRT (rectangulaire)

if Data == "small_instance" :
    longueur = 800 # en metres, longueur de la zone de service DRT (rectangulaire)
    largeur = 400 # en metres, largeur de la zone de service DRT (rectangulaire)


largeur_degres = largeur / (111.11 * 10**3)
longueur_degres = longueur / (111.11 * np.abs(np.cos(math.radians(lat)))* 10**3)
########################################################################

vitesse_DRT = 30 # en km/h, vitesse moyenne des vehicules DRT

# liste des stop_id des stations DRT

## Intervenant dans le fichier 'PCC_totaltimes_DataFrames.py' :
ray_max = 10000 # en metres, rayon max auquel doivent appartenir les stations pour etre une destination du centroide
ray_min = 2000 # en metres, rayon min auquel doivent appartenir les stations pour etre une destination du centroide


## Intervenant dans 'Res_DataFrames.py' :
h0_str = ['1_min', '2_min', '4_min', '16_min', '32_min', '64_min'] # format String pour le nom des fichiers
# idx_h = 0
h_str = h0_str[idx_h] # valeur de h actuelle


################################################################################################
# SAVOIR OÙ PLACER LES DRT GRÂCE À L'HEURISTIQUE
################################################################################################

# Chemin vers votre fichier .txt
chemin_repertoire = os.path.normpath('./Results_{}/Placement_DRT'.format(Data))
chemin_fichier = os.path.join(chemin_repertoire, 'DRT_placement_stops.txt')

if not os.path.isdir(chemin_repertoire):
    os.mkdir(chemin_repertoire)

if os.path.isfile(chemin_fichier):
    # Lire le fichier .txt
    with open(chemin_fichier, 'r') as file:
        lines = file.readlines()
    nb_DRT = int(nb_DRT)
    # Extraire la liste à la ligne numéro m
    if nb_DRT  < len(lines):
        liste_stations_DRT = lines[nb_DRT]
    else:
        print("Nous n'avons pas calculé l'heuristic pour ", nb_DRT , " DRT")
else:
    print("Le fichier n'existe pas : ", chemin_fichier)

################################################################################################
