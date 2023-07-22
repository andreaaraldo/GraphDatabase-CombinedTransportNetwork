import subprocess
import pandas as pd
import os
import Parameters
import sys

# to run this code, make sure to set : show_fig = False in Heuristic_simple2.py
# so the code runs without plotting the graphs

# Lire la valeur mise à jour de nb_centr_init depuis le fichier
def read_nb_centr_init():
    with open('nb_centr_init.txt', 'r') as file:
        value = int(file.read())
    return value

Data = Parameters.Data
nb_DRT = Parameters.nb_DRT

# Initialisation de nb_centr en fonction de la taille de la ville 
path_centroids = os.path.normpath('{}/centroids.txt'.format(Data))
centroids = pd.read_csv(path_centroids)
centroids = centroids.drop_duplicates(subset='centroid_id')
nb_centr_total = centroids.shape[0]
nb_centr = int(nb_centr_total/15)

# On récupère les informations sur les stops :
path_stops = os.path.normpath('{}/stops.txt'.format(Data))
stops = pd.read_csv(path_stops)
nb_stops = stops.shape[0]
print('nb_stops = ', nb_stops)

if nb_DRT >= nb_stops-6 : #6 : chiffre pris empiriquement pour small_instance --> ne marche pas au delà
    print("Il faut que nb_DRT soit inférieur à nb_stops = {}. Or nb_DRT = {} >= {}".format(nb_stops, nb_DRT, nb_stops))
    sys.exit()

for nb_DRT in range(1, min(nb_stops-6, 30)):
    nb_DRT = str(nb_DRT)
    nb_centr = str(nb_centr)
    print("##########################\n \n Executing Heuristic_simple2.py... For nb_DRT = {} \n \n##########################".format(nb_DRT))
    # Exécuter le fichier
    #subprocess.run(['python3', 'Heuristic_simple2.py', nb_centr, nb_DRT], check=True)
    process = subprocess.Popen(['python3', 'Heuristic_simple2.py', nb_centr, nb_DRT], stdout=subprocess.PIPE)
    output, _ = process.communicate()

    # On modifie la valeur de read_nb_init() pour la prochaine itération
    nb_centr = read_nb_centr_init()