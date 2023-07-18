import subprocess

# Liste des fichiers à exécuter dans l'ordre, après avoir changé *liste_stations_DRT* dans Parameters.py
fichiers = ['Load_DRT.py', 'PCC_optimized.py', 'Res_DataFrames.py', 'Create_Graph_acc_DRT.py']

# Parcourir la liste des fichiers et les exécuter à la suite
for fichier in fichiers:
    print("##########################\n \n Executing ", fichier, "... \n \n##########################")
    # Exécuter le fichier
    subprocess.run(['python3', fichier], check=True)