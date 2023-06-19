'''
AVANT D'EXECUTER CE FICHIER :
- changer *liste_stations_DRT* dans Parameters.py avec le placement des DRT (choisir l'heuristique)
'''

import subprocess
import Parameters
import matplotlib.pyplot as plt

# Liste des fichiers à exécuter dans l'ordre, après avoir changé *liste_stations_DRT* dans Parameters.py
fichiers = ['Load_DRT.py', 'PCC_optimized.py', 'Res_DataFrames.py', 'Create_Graph_acc_DRT.py']

# Parcourir la liste des fichiers et les exécuter à la suite
for fichier in fichiers:
    print("##########################\n \n Executing ", fichier, "... \n \n##########################")
    # Exécuter le fichier
    subprocess.run(['python3', fichier], check=True)

#Renommer les fichiers qui viennent d'être créés afin de leur donner du sens
h = Parameters.h
nb_DRT = Parameters.nb_DRT