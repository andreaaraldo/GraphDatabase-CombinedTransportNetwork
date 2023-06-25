import subprocess
import os
import Parameters
import pandas as pd
import matplotlib.pyplot as plt


nb_DRT = Parameters.nb_DRT
Data = Parameters.Data

################################################################################
# Import des données
################################################################################
#Création d'un dataframe avec les résultats calculés
path_res = os.path.normpath('Results_{}/res/res_1_min_{}DRT.txt'.format(Data,nb_DRT))
res = pd.read_csv(path_res)
res.head()

# Exécuter le fichier "mon_script.py" en utilisant Python
path_centroids = os.path.normpath('./{}/centroids.txt'.format(Data))

data_centroids = pd.read_csv(path_centroids)
data_centroids.head()

data_centroids_drop = data_centroids.drop_duplicates(subset='centroid_id')

path_stops = os.path.normpath('{}/stops.txt'.format(Data))
path_stops_drt = os.path.normpath('./Stations/list_station_id_{}DRT.txt'.format(nb_DRT))

stops = pd.read_csv(path_stops)
stops_drt = pd.read_csv(path_stops_drt)

# Fusionner les deux DataFrames sur la colonne 'stop_id'
stops_filtered = pd.merge(stops, stops_drt[['station_list']], how='inner', left_on='stop_id', right_on='station_list')

# Fusionner data_centroids_drop avec res_1_min sur la colonne 'centroid_id'
merged_data = data_centroids_drop.merge(res, left_on='centroid_id', right_on='centroid')

################################################################################
#calcul inaccessibilité moyenne 
################################################################################
somme_inacc = res['inaccessibilite'].sum()
nb_centroids = res.shape[0]
print()
inacc_moy = somme_inacc/nb_centroids

################################################################################
# Tracer le graphique
################################################################################
# Sélectionner les colonnes nécessaires pour tracer le graphique
x = merged_data['centroid_lon']
y = merged_data['centroid_lat']
c = merged_data['inaccessibilite']

# Tracer le graphique
plt.scatter(x, y, c=c, alpha=0.5, marker='o', label="Centroids")
# Ajouter une légende pour la couleur
plt.colorbar()
#res_1_min_top10['inaccessibilite']
plt.scatter(stops['stop_lon'], stops['stop_lat'], c='black', label = 'Stops', alpha = 0.5)
plt.xlabel('Longitude')
plt.ylabel('Latitude')

if nb_DRT > 0 :
    plt.scatter(stops_filtered['stop_lon'], stops_filtered['stop_lat'], c='orange', label="Stop DRT")

# Ajouter les étiquettes des points (stop_id) en gras et en rouge
for i in range(len(stops_filtered)):
    plt.annotate(stops_filtered['stop_id'][i], xy=(stops_filtered['stop_lon'][i], stops_filtered['stop_lat'][i]), textcoords='offset points', xytext=(0,5), ha='center', fontweight='bold')
plt.legend()
plt.title('Inaccessibilité pour {}DRT \n Moyenne inaccessibilitée = {:.2f}'.format(nb_DRT, inacc_moy))
plt.show()






################################################################################
#calcul accessibilité moyenne 
################################################################################
somme_acc = res['accessibilite'].sum()
nb_centroids = res.shape[0]
print()
acc_moy = somme_acc/nb_centroids

################################################################################
# Tracer le graphique
################################################################################
# Sélectionner les colonnes nécessaires pour tracer le graphique
x = merged_data['centroid_lon']
y = merged_data['centroid_lat']
c = merged_data['accessibilite']

# Tracer le graphique
plt.scatter(x, y, c=c, alpha=0.5, marker='o', label="Centroids")
# Ajouter une légende pour la couleur
plt.colorbar()
#res_1_min_top10['accessibilite']
plt.scatter(stops['stop_lon'], stops['stop_lat'], c='black', label = 'Stops', alpha = 0.5)
plt.xlabel('Longitude')
plt.ylabel('Latitude')

if nb_DRT > 0 :
    plt.scatter(stops_filtered['stop_lon'], stops_filtered['stop_lat'], c='orange', label="Stop DRT")

# Ajouter les étiquettes des points (stop_id) en gras et en rouge
for i in range(len(stops_filtered)):
    plt.annotate(stops_filtered['stop_id'][i], xy=(stops_filtered['stop_lon'][i], stops_filtered['stop_lat'][i]), textcoords='offset points', xytext=(0,5), ha='center', fontweight='bold')
plt.legend()
plt.title('Accessibilité pour {}DRT \n Moyenne accessibilitée = {:2f}'.format(nb_DRT, acc_moy))
plt.show()