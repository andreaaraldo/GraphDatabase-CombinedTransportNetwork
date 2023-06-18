'''
AVANT D'EXECUTER CE FICHIER :
- changer *liste_stations_DRT* dans Parameters.py avec le placement des DRT
'''

import subprocess
import os
import Parameters
import matplotlib.pyplot as plt

# Liste des fichiers à exécuter dans l'ordre, après avoir changé *liste_stations_DRT* dans Parameters.py
fichiers = ['Load_DRT.py', 'PCC_optimized.py', 'Res_DataFrames.py', 'Load_Graph_acc_DRT.py']

# Parcourir la liste des fichiers et les exécuter à la suite
for fichier in fichiers:
    print("##########################\n \n Executing ", fichier, "... \n \n##########################")
    # Exécuter le fichier
    subprocess.run(['python3', fichier], check=True)

#Renommer les fichiers qui viennent d'être créés afin de leur donner du sens
h = Parameters.h
nb_DRT = Parameters.nb_DRT


'''
#### h_1_min #####
Results = os.path.normpath('./Results')
ancien_nom_h = "h_{}_min".format(int(h/60))
chemin_ancien_h = os.path.join(Results, ancien_nom_h)

nouveau_nom_h = "h_{}_min_{}DRT".format(int(h/60), nb_DRT )
chemin_nouveau_h = os.path.join(Results, nouveau_nom_h)

os.rename(chemin_ancien_h, chemin_nouveau_h)

#### res #####
res = os.path.normpath('/Results/res')
#ancien_nom_res = "res_{}_min.txt".format(int(h/60))
ancien_nom_res = "res_1_min.txt"
chemin_ancien_res = os.path.join(res, ancien_nom_res)

nouveau_nom_res = "res_{}_min_{}DRT.txt".format(int(h/60), nb_DRT)
chemin_nouveau_res = os.path.join(res, nouveau_nom_res)

os.rename(chemin_ancien_res, chemin_nouveau_res)
'''