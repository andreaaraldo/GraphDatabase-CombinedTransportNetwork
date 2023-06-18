import subprocess

# Liste des fichiers à exécuter dans l'ordre
fichiers = ['Grid_Distances.py', 'DataFrame_stoptimes.py', 'Reduce_Centroid_Stop.py', 'Load_Graph_Centroids_optimized.py']

# Parcourir la liste des fichiers et les exécuter à la suite
for fichier in fichiers:
    print("##########################\n \n Executing ", fichier, "... \n \n##########################")
    # Exécuter le fichier
    subprocess.run(['python3', fichier], check=True)
