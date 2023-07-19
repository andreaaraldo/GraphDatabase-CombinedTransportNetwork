import subprocess
import os
import Parameters

Data = Parameters.Data
nb_DRT = Parameters.nb_DRT

# Liste des fichiers à exécuter dans l'ordre, après avoir changé *liste_stations_DRT* dans Parameters.py
fichiers = ['Heuristic_iter.py','Load_DRT.py', 'PCC_optimized.py', 'Res_DataFrames.py', 'Create_Graph_acc_DRT.py']

res_0DRT = os.path.normpath('Results_{}/res/res_1_min_0DRT.txt'.format(Data))
if not os.path.exists(res_0DRT) and nb_DRT != 0:
        print("Il faut d'abord run 2_Run_PCC_DRT.py pour nb_DRT = 0 (à changer dans Parameters.py)")
else : 
    # On ne calcule pas l'heuristic si l'on n'a jamais calculé res dans DRT 
    if nb_DRT == 0 :
        fichiers = ['PCC_optimized.py', 'Res_DataFrames.py', 'Create_Graph_acc_DRT.py']
    # Parcourir la liste des fichiers et les exécuter à la suite
    for fichier in fichiers:
        print("##########################\n \n Executing ", fichier, "... \n \n##########################")
        # Exécuter le fichier
        subprocess.run(['python3', fichier], check=True)