import numpy as np
import pandas as pd
import matplotlib as matplotlib
import matplotlib.pyplot as plt
import math
import time
from pyproj import Geod
# !pip install shapely
# !pip install geographiclib
import shapely
from shapely.geometry import Polygon, LineString, Point
import geographiclib
from geographiclib.geodesic import Geodesic
import Parameters
import os
import sys
import matplotlib.pyplot as plt

# variables
h = Parameters.h

'''
# Vérifier le nombre d'arguments passés
if len(sys.argv) != 2:
    print("Usage: python Load_DRT.py nombre_DRT")
    sys.exit(1)
'''
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
# Heuristique simple
####################################################

#on crée le dossier (s'il n'existe pas encore) qui recense les meilleurs emplacements pour mettre les DRT (suivant l'heuristique) 

filename = os.path.normpath('./Heuristic/DRT_heuristique_simple.txt')

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
print(res.head())


somme_inacc = res['accessibilite'].sum()
print(somme_inacc)
nb_centroids = res.shape[0]
print(nb_centroids)
print(somme_inacc/nb_centroids)

# On associe les accessibilités calculées aux stops :
path_stops = os.path.normpath('Data/stops.txt')
stops = pd.read_csv(path_stops)

# Obtenir les identifiants des stops
stop_id = stops['stop_id'].tolist()

# Filtrer les lignes du dataframe res_1_min_sansDRT en fonction des identifiants des stops
res_stops = res[res['centroid'].isin(stop_id)]
#print(res_1_min_sansDRT_stops)

# Trier le DataFrame par ordre croissant en fonction de la colonne accessibilite
res_stops_sorted = res_stops.sort_values('accessibilite')
print('dataframe trié : ', res_stops_sorted.head())

# Extraire les m premières lignes du DataFrame trié
res_min_acc = res_stops_sorted.head(nb_DRT)
res_max_acc = res_stops_sorted.tail(nb_DRT)

placement_DRT = res_min_acc['centroid'].tolist()
placement_DRT_acc = res_min_acc['accessibilite'].tolist()
placement_DRT_acc_max = res_max_acc['accessibilite'].tolist()

#################################################################################
# Evaluer la répartion des centroids en fonction de leur accessibilité
#print(placement_DRT)
#print(placement_DRT_acc)
#print(placement_DRT_acc_max)
'''
plt.figure(figsize=(7,2))
plt.scatter(res_stops_sorted['accessibilite'], [0]*len(res_stops_sorted['accessibilite']), alpha = 0.3, c = res_stops_sorted['accessibilite'])
plt.title("Répartion de l'accessibilitée dans le graphe")
plt.show()
'''
#################################################################################

# Mettre ces résultats dans le fichier à la ligne n° nb_DRT
ecrire_ligne(filename, nb_DRT, placement_DRT)


#ROYAN 
#m = 10 : [659, 823, 822, 656, 576, 495, 577, 616, 617, 657]
#m = 5 : [495, 577, 616, 617, 657]