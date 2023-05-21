# GraphDatabase-CombinedTransportNetwork
Please read [our article](https://arxiv.org/abs/2210.08327) to know more about the problem of accessibility, demand-responsive transit and Neo4j.

N.B. All file paths are expressed as in Windows. When you run the code you might have errors related to this. You just need to correct for your system.

## Prerequirements
Download and install `neo4j Desktop`. We suggest you to use Anaconda. You can install the required Python package from Anaconda. The Python libraries you need to install are:

- shapely
- geographiclib
- geopandas
- neo4j (or neo4j-python-driver)
- numpy
- pandas
- matplotlib
- time
- os
- math



## Objectifs
Les fichiers **.py** permettent la création d'un graphe combinant un réseau de transport en commun dont on a téléchargé les données au format **GTFS** et un service de transport à la demande **Demand Responvie Transit** (DRT).

You need to understand the GTFS data structure before using this code.

They allow to compute accessibility values for all locations, along with additional information (see section at the end)

## Définitions
- **GTFS** : format de donnée utilisé pour l'échange de données de transport. Les données sont regroupées dans différents fichiers textes. Description de ce format : https://developers.google.com/transit/gtfs/reference/
- Service **DRT** : service de transport en commun à la demande dont le principe est que le véhicule DRT (= Demand-Responsive Transit) adapte sa route aux requêtes des usagers. Le modèle de service DRT présenté dans l'article "Assessing transportation accessibility equity via open data" de Amirhesam Badeanlou, Andrea Araldo et Marco Diana est utilisé.
- **Accessibilité** : cette métrique permet de donner une idée de la qualité du service de transport d'une zone/centroïde. À chaque zone (= origine) est associé un ensemble de destinations potentielles. On récupère alors le temps total des plus-court-chemins pour chaque paire origine-destination. La somme de ces temps totaux est appelée **inaccessibilité**, son inverse étant l'**accessibilité**. Les destinations potentielles d'un centroïde sont les stations comprises entre deux rayons (paramètres ray_max et ray_min dans le fichier **Parameters.py**).

### Construction du graphe
- Le réseau de transport en commun fixe (données GTFS) est représenté dans le graphe par les noeuds **Stop** (stations physiques) et **Stoptime** (horaires d'arrêts) et les relations **PRECEDES** (succession des arrêts, sens et direction du train), **CORRESPONDANCE** et **LOCATED_AT** (horaire d'arrêt localisé à une station).
- Les positions de départ des usagers sont représentées par les noeuds **Centroid** auquel est associé un horaire de départ (le même pour tous).
- La posibilité de se déplacer à pieds d'un centroïde à une station est représentée par la relation **WALK**.
- Le réseau de transport à la demande est modélisé selon les formules de l'article cité précédemment. La possibilité de prendre un véhicule DRT pour aller à une station à partir d'un centroïde est représentée par la relation **DRT**.
- À chaque relation (= arc dans le graphe) est attribué la propriété **inter_time** : le temps nécessaire à effectué le trajet représenté par l'arc. C'est cette propriété qui va être considérée comme le coût lors de la recherche d'un plus-court-chemin.



## Etapes
### 1°) Choisir un réseau de transport.
Télécharger ses données au format GTFS et les importer dans le dossier **Data** en remplaçant ceux existant déjà (correspondant aux données GTFS de Royan).

### 2°) Exécuter le fichier **Grid_Centroids.py**.
This script takes `stops.txt` as input and effectue le pavage de la ville et récupère les coordonnées des centroïdes. Il calcule les distances stations-centroïdes et les sauvegarde dans le fichier **distances.txt** dans le dossier **Data**. Il sauvegarde également les coordonnées des centroïdes et celles des stations dans les fichiers **pos_centroids.txt** et **pos_stations.txt** dans le dossier **Data**.

### 3°) Exécuter le fichier **DataFrame_stoptimes.py**.
This script takes `trips.txt` and `stop_times.txt` as input and creates **df.txt** dans le dossier **Data**, which contains summarized information about les **routes** et **trips**. Each line represents a stop_time with the following information: trip_id, route_id, departure_time etc.

### 4°) Pour les centroïdes :
In `Parameters.py` modify the following values
- **rayon_exclusif**: if a centroid does not have any station within this distance, it will be discarded.
- **vitesse_walk**, **departure_time**, **rayon_walk**: these values dermine the speed of walking, the departure time and the maximum walkable distance.

Exécuter le fichier **Reduce_Centroid_Stop.py**.
Ce fichier supprime les centroïdes trop isolés par rapport aux stations (par rapport au paramètre `rayon-exclusif`. Le fichier **centroids.txt** est créé dans le dossier **Data**, il contient les informations utiles sur les futurs noeuds Centroids.

### 5°) Ouvrir une base de données dans Neo4j :
This operations in neo5j must be done only once (it might take a long time). For all the next runs, you should just ensure that neo4j is up and running.

- Ouvrir Neo4j Desktop
- Créer un nouveau Projet : "+ New"

![image](https://user-images.githubusercontent.com/93777543/194310066-a3fe87d4-088c-4836-bf36-2856d0059a9a.png)
- Ajouter une base : "+ Add" > Local DBMS

The password must be the same as in the script `Load_Graph_Centroids.py`

![image](https://user-images.githubusercontent.com/93777543/194309986-75e32c4b-a5ab-4ed8-a3f9-59696b2dd426.png)
- Choisir la version 4.4.0

![image](https://user-images.githubusercontent.com/93777543/194310697-fa2fab7e-173c-4d80-b647-367f6f5d7e16.png)
- Click on your project > Plugins > Ajouter les plugins **APOC**, **Graph Data Science Library** et **Neo4jStreams**

![image](https://user-images.githubusercontent.com/93777543/194311329-618a0cab-edef-4a9e-b610-2bfcddb8b038.png)
- Démarrer la base, by clicking `Start`

![image](https://user-images.githubusercontent.com/93777543/194312939-3691190b-27a6-4c61-ad60-1b04e15f5c5b.png)
- Ouvrir la base une fois démarrée, by clicking `Open`

![image](https://user-images.githubusercontent.com/93777543/194313052-ba71a5e7-3d8c-44b7-ad57-39fba84be0a3.png)

![image](https://user-images.githubusercontent.com/93777543/194313133-71ccc8dc-62e6-431b-b9d5-bcf8a8ca3fbd.png)

Please annotate the url showed in the Connection Status of neo4j and report it to `Load_Graph_Centroids.py`.

### 6°) Exécuter le fichier **Load_Graph_Centroids.py**.

"""
in order to use load_csv with local files, make sure to do as follows:

1.Find the neo4j.conf file for your Neo4j installation.

2.Comment this line(By adding # in the start):
dbms.directories.import=import

3.Uncomment this line to allow CSV import from file URL:
#dbms.security.allow_csv_import_from_file_urls=true

4.Restart Neo4j
"""

Ce fichier crée la base du graphe dans Neo4j, c'est-à-dire le réseau à partir des données GTFS + les noeuds Centroids et leurs relations WALK avec des Stoptimes. This script may take some time. You will see in neo4j that nodes are being added during the process (check "Node labels" on the left of the neo4j interface").

### 7°) Horaire de départ des centroïdes :
On peut modifier l'horaire de départ des centroïdes (par rapport à la valeur initiale écrite dans `departure_time` in `Parameters.py`) après avoir créé la base du graphe sans devoir refaire tout le graphe. Le fichier **Change_departure_time_centroid.py** permet de modifier cet horaire et de re-créer les nouvelles relations WALK impactées par cette modification. Il faut modifier le paramètre **new_departure_time** dans le fichier **Parameters.py**, puis exécuter le fichier **Change_departure_time_centroid.py**.
Cette modification est à effectuer avant les étapes suivantes.

### 8°) Ajouter le service DRT au graphe :
- Choisir les stations qui bénéfieront d'un service DRT = relever les identifiants de ces stations from `stops.txt`. Modifier le paramètre **liste_stations_DRT** dans le fichier **Parameters.py** en ajoutant les identifiants (**stop_id**) des stations choisies.
- Choisir les valeurs des paramètres relatifs au service DRT : **densité** (how many people per Km / h live in that zone), **longueur**, **largeur** (of the area in which our DRT service will work), **vitesse_DRT** et **h** (the inter-time between a DRT departure and the next) dans `Parameters.py`
- Exécuter enfin le fichier **Load_DRT.py**.
- Le graphe du réseau combiné est terminé.

### 9°) Plus-court-chemins (PCC) :
- Modifier les valeurs des rayons délimitant la zone à partir d'un centoïde à laquelle doit appartenir une station pour être une destination : **ray_min** et **ray_max** dans le fichier **Parameters.py**.
- Exécuter le fichier **PCC_totaltimes_DataFrames.py**
Ce fichier trouve les PCC entre centroïdes (origine) et stations (destinations). Il récupère des informations sur ces PCC et les regroupe dans un dataframe. Il y a un dataframe par origine (centroïde) : **centroid_{centroid_id}.txt** dans le dossier **Results/h_{valeur de h en minute}_min**. Si il n'y a pas de chemin trouvé dans le graphe, on considère que l'on se rend à la destination directement à pieds (vol d'oiseau).

### 10°) Résultats :
Exécuter le fichier **Res_DataFrames.py**. Ce fichier résume les résultats précédemment obtenus pour chaque centroïde dans un fichier **res_{valeur de h en minute}_min.txt**. In this file, we have one line per each centroid, with the indication of the accessibiliy value (as computed in [our article](https://arxiv.org/abs/2210.08327)).

## Structure des fichiers sur les PCC et les résultats
### centroid_{centroid_id}.txt:
1 ligne correspond à une destination accessible depuis le centroïde, colonnes :
- **destination** : stop_id de la destination.
- **total_time** : temps total du trajet (coût total du PCC ou temps direct à pieds).
- **transport** : mode de transport choisi au départ du centroïde : arc WALK ou arc DRT, 'DRT/WALK' si le choix de l'arc ne change pas le temps total.
- **correspondance** : nombre de fois que l'on a emprunté un arc CORRESPONDANCE dans le trajet.
- **1st_station** : stop_id de la première station atteinte.
- **time_to_1st_station** : temps nécessaire pour atteindre la première station.
- **walking_time** : temps sur l'arc WALK si emprunté, None sinon.
- **drt_time** : temps sur l'arc DDRT si emprunté, None sinon.
- **drt_waiting_time** : temps d'attente pour le véhicule DRT si DRT emprunté, None sinon.
- **direct_walking_time** : temps pour atteindre la destination directement à pieds.

### Structure of metrics file
{{Anchor|structure-metrics}}
res_{valeur de h en minute}_min.txt :
1 ligne correspond à un centroïde, colonnes :
- **centroid** : centroi_id correspondant au centroïde.
- **nb_destinations** : nombre de destinations accessibles au centroïde.
- **trajets** : nombre de trajets trouvés.
- **trajets_ok** : nombre de trajets raisonnables trouvés. Un trajet est raisonnables lorsque le temps total du PCC (trajet) est inférieur au temps nécessaire pour atteindre la destination directement à pieds.
- **nb_station_DRT** : nombre de trajets dont la première station atteinte est une station DRT.
- **DRT** : nombre de trajets ayant emprunté l'arc DRT.
- **DRT_ok** :  nombre de trajets raisonnables ayant emprunté l'arc DRT.
- **WALK_to_station_DRT** : nombre de trajets ayant emprunté l'arc WALK pour atteindre une station DRT.
- **WALK** : nombre de trajets ayant emprunté l'arc WALK.
- **somme** : somme des temps totaux de chaque trajet raisonnable, si aucun trajet trouvé : temps pour atteindre la destination directement à pieds.
- **somme_moyennée** : somme moyennées sur le nombre de destinations accessibles.
- **accessibilite** : accessibilité = 1/somme

