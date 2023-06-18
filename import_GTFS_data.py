## Importer une nouvelle base de données et la configurer
import subprocess


### 1°) Choisir un réseau de transport.
# Télécharger ses données au format GTFS et les importer dans le dossier **Data**
# en remplaçant ceux existant déjà (correspondant aux données GTFS de Royan).


### 2°) Exécuter le fichier **Grid_Centroids.py**.
# This script takes `stops.txt` as input and effectue le pavage de la ville et récupère
# les coordonnées des centroïdes. Il calcule les distances stations-centroïdes et les 
# sauvegarde dans le fichier **distances.txt** dans le dossier **Data**. Il sauvegarde 
# également les coordonnées des centroïdes et celles des stations dans les fichiers 
# **pos_centroids.txt** et **pos_stations.txt** dans le dossier **Data**.

grid_centroids = "Grid_Centroids.py"
subprocess.call(["python", grid_centroids])

### 3°) Exécuter le fichier **DataFrame_stoptimes.py**.
# This script takes `trips.txt` and `stop_times.txt` as input and creates **df.txt** dans
# le dossier **Data**, which contains summarized information about les **routes** et **trips**. 
# Each line represents a stop_time with the following information: trip_id, route_id, departure_time etc.

DataFrame_stoptimes = "DataFrame_stoptimes.py"
subprocess.call(["python", DataFrame_stoptimes.py])


### 4°) Pour les centroïdes :
'''
In `Parameters.py` modify the following values
- **rayon_exclusif**: if a centroid does not have any station within this distance, it will be discarded.
- **vitesse_walk**, **departure_time**, **rayon_walk**: these values dermine the speed of walking, the departure time and the maximum walkable distance.
'''

#Exécuter le fichier **Reduce_Centroid_Stop.py**.
#Ce fichier supprime les centroïdes trop isolés par rapport aux stations (par rapport au paramètre 
# `rayon-exclusif`. Le fichier **centroids.txt** est créé dans le dossier **Data**, il contient les 
# informations utiles sur les futurs noeuds Centroids.

Reduce_Centroid_Stop = "Reduce_Centroid_Stop.py"
subprocess.call(["python", Reduce_Centroid_Stop.py])

### 5°) Ouvrir une base de données dans Neo4j :
# This operations in neo5j must be done only once (it might take a long time). For all the next runs, 
# you should just ensure that neo4j is up and running.

# Demande à l'utilisateur s'il a déjà ouvert une base de données Neo4j
reponse = input("Avez-vous déjà ouvert une base de données Neo4j pour cette ville ? (O/N) ")

if reponse.lower() == "o":
    print("Vérifiez qu'elle tourne bien")
elif reponse.lower() == "n":
    print("""- Ouvrir Neo4j Desktop
    - Créer un nouveau Projet : "+ New"
    - Ajouter une base : "+ Add" > Local DBMS

    The password must be the same as in the script `Load_Graph_Centroids.py`
    - Choisir la version 4.4.0
    - Click on your project > Plugins > Ajouter les plugins **APOC**, **Graph Data Science Library** et **Neo4jStreams**
    - Démarrer la base, by clicking `Start`
    - Ouvrir la base une fois démarrée, by clicking `Open`

    Please annotate the url showed in the Connection Status of neo4j and report it to `Load_Graph_Centroids.py`.""")
else:
    print("Réponse non valide. Veuillez répondre par 'O' ou 'N'.")

### 6°) Exécuter le fichier **Load_Graph_Centroids.py**.
# Ce fichier crée la base du graphe dans Neo4j, c'est-à-dire le réseau à partir des données GTFS + 
# les noeuds Centroids et leurs relations WALK avec des Stoptimes. This script may take some time. You will 
# see in neo4j that nodes are being added during the process (check "Node labels" on the left of the neo4j interface").

print("Executing Load_Graph_Centroids.py... This should take >30 min ")
Load_Graph_Centroids = "Load_Graph_Centroids.py"
subprocess.call(["python", Load_Graph_Centroids.py])

### 7°) Horaire de départ des centroïdes :
# On peut modifier l'horaire de départ des centroïdes (par rapport à la valeur initiale écrite dans `departure_time` 
# in `Parameters.py`) après avoir créé la base du graphe sans devoir refaire tout le graphe. Le fichier 
# **Change_departure_time_centroid.py** permet de modifier cet horaire et de re-créer les nouvelles relations WALK
# impactées par cette modification. Il faut modifier le paramètre **new_departure_time** dans le fichier **Parameters.py**, 
# puis exécuter le fichier **Change_departure_time_centroid.py**.
# Cette modification est à effectuer avant les étapes suivantes.

### 8°) Ajouter le service DRT au graphe :
"""
- Choisir les stations qui bénéfieront d'un service DRT = relever les identifiants de ces stations from `stops.txt`. Modifier le paramètre **liste_stations_DRT** dans le fichier **Parameters.py** en ajoutant les identifiants (**stop_id**) des stations choisies.
- Choisir les valeurs des paramètres relatifs au service DRT : **densité** (how many people per Km / h live in that zone), **longueur**, **largeur** (of the area in which our DRT service will work), **vitesse_DRT** et **h** (the inter-time between a DRT departure and the next) dans `Parameters.py`
- Exécuter enfin le fichier **Load_DRT.py**.
- Le graphe du réseau combiné est terminé.
"""

### 9°) Plus-court-chemins (PCC) :
"""
- Modifier les valeurs des rayons délimitant la zone à partir d'un centoïde à laquelle doit appartenir une station pour être une destination : **ray_min** et **ray_max** dans le fichier **Parameters.py**.
- Exécuter le fichier **PCC_totaltimes_DataFrames.py**
Ce fichier trouve les PCC entre centroïdes (origine) et stations (destinations). Il récupère des informations sur ces PCC et les regroupe dans un dataframe. Il y a un dataframe par origine (centroïde) : **centroid_{centroid_id}.txt** dans le dossier **Results_{}/h_{valeur de h en minute}_min**. S'il n'y a pas de chemin trouvé dans le graphe, on considère que l'on se rend à la destination directement à pieds (vol d'oiseau).
"""

### 10°) Résultats :
# Exécuter le fichier **Res_DataFrames.py**. Ce fichier résume les résultats précédemment obtenus pour 
# chaque centroïde dans un fichier **res_{valeur de h en minute}_min.txt**. In this file, we have one 
# line per each centroid, with the indication of the accessibiliy value (as computed in [our article]
# (https://arxiv.org/abs/2210.08327)).

print("Executing Res_DataFrames.py... This should take __ min ")
Res_DataFrames = "Res_DataFrames.py"
subprocess.call(["python", Res_DataFrames.py])

print("The database is ready for use !")