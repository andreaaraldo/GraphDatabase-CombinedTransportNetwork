# GraphDatabase-CombinedTransportNetwork


## Descriptions des fichiers et dossiers

**Data** : dossier contenant les fichiers .txt des données GTFS du réseau de transport en commun choisi. 

**Results** : dossier contenant les résultats obtenus après l'exécution du fichier **PCC_totaltimes_DataFrames.py**.

**Stations** : dossier contenant les identifiants des stations choisies pour bénéficier du service DRT + les listes des centroïdes situés dans la zone de service DRT de ces stations.

**Change_departure_time_centroid.py** : permet de changer l'horaire de départ de tous les centroïdes.

**Grid_Centroids.py** : effectue le pavage de la ville choisie, récupère les centroïdes et les distances centroïde-station. Crée les fichiers **centroids.txt**, **df.txt**, **distances.txt**, **position.txt**.

**Load_DRT.py** : calcule les temps d'attente et de trajet des véhicules DRT, crée les relations DRT dans le graphe Neo4j ouvert.

**Load_Graph_Centroids.py** : crée le graphe de base contenant les noeuds *Stop*, *Stoptime* et *Centroid*, ainsi que les relations *LOCATED_AT*, *PRECEDES*, *CORRESPONDANCE*, *WALK*.

**PCC_totaltimes_DataFrames.py** : recherche les PCC entre les centroïdes situés dans une zone DRT et les destinations se trouvant dans un certain rayon.


## 
### 1°) Choisir un réseau de transport, télécharger ses données au format GTFS et les importer dans le dossier **Data**.

### 2°) Exécuter le fichier **Grid_Centroids.py**. (long)

### 3°) Ouvrir une base de données dans Neo4j :

- Ouvrir Neo4j Desktop

- Créer un nouveau Projet : "+ New"

![image](https://user-images.githubusercontent.com/93777543/194310066-a3fe87d4-088c-4836-bf36-2856d0059a9a.png)

- Ajouter une base : "+ Add" > Local DBMS

![image](https://user-images.githubusercontent.com/93777543/194309986-75e32c4b-a5ab-4ed8-a3f9-59696b2dd426.png)

- Choisir la version 4.4.0

![image](https://user-images.githubusercontent.com/93777543/194310697-fa2fab7e-173c-4d80-b647-367f6f5d7e16.png)

- Ajouter les plugins **APOC**, **Graph Data Science Library** et **Neo4jStreams**

![image](https://user-images.githubusercontent.com/93777543/194311329-618a0cab-edef-4a9e-b610-2bfcddb8b038.png)

- Démarrer la base

![image](https://user-images.githubusercontent.com/93777543/194312939-3691190b-27a6-4c61-ad60-1b04e15f5c5b.png)

- Ouvrir la base une fois démarrée

![image](https://user-images.githubusercontent.com/93777543/194313052-ba71a5e7-3d8c-44b7-ad57-39fba84be0a3.png)

![image](https://user-images.githubusercontent.com/93777543/194313133-71ccc8dc-62e6-431b-b9d5-bcf8a8ca3fbd.png)


### 4°) Exécuter le fichier **Load_Graph_Centroids.py**.

### 5°) Choisir les stations qui bénéfieront d'un service DRT. Relever les identifiants (**stop_id**) et les écrire en colonne dans le fichier **list_station_id.txt** dans le dossier **Stations**.

### 6°) Modifier les valeurs dans le fichier **parameters.py**.

### 7°) 










