import os
import Parameters
import pandas as pd
import matplotlib.pyplot as plt
import ast

nb_DRT = Parameters.nb_DRT
Data = Parameters.Data
liste_stations = Parameters.liste_stations_DRT
show = True 

################################################################################
# Import des données
################################################################################
#Création d'un dataframe avec les résultats calculés
## Avec nb_DRT DRT

path_res = os.path.normpath('Results_{}/res/res_1_min_{}DRT.txt'.format(Data, nb_DRT))
res = pd.read_csv(path_res)
#print('res : \n', res.head())
## Sans DRT 
path_res_0DRT = os.path.normpath('Results_{}/res/res_1_min_0DRT.txt'.format(Data))
res_0DRT = pd.read_csv(path_res_0DRT)
#print('res_0DRT : \n', res_0DRT.head())
# Filtrage des lignes de res_0DRT
res_0DRT = res_0DRT[res_0DRT['centroid'].isin(res['centroid'])]
#print('res_0DRT : \n', res_0DRT.head())

path_centroids = os.path.normpath('./{}/centroids.txt'.format(Data))
data_centroids = pd.read_csv(path_centroids)
data_centroids_drop = data_centroids.drop_duplicates(subset='centroid_id')

path_stops = os.path.normpath('{}/stops.txt'.format(Data))

stops = pd.read_csv(path_stops)

############################################################
# Filtrer le DataFrame

# Conversion de la chaîne en liste d'entiers
liste_stations = ast.literal_eval(liste_stations)
stops_filtered = stops[stops['stop_id'].isin(liste_stations)]
stops_filtered = stops_filtered.reset_index(drop=True)
#print('stops_filtered : \n', stops_filtered.head())

# Fusionner data_centroids_drop avec res sur la colonne 'centroid_id'
merged_data = data_centroids_drop.merge(res, left_on='centroid_id', right_on='centroid')
# Sans DRT 
merged_data_0DRT = data_centroids_drop.merge(res_0DRT, left_on='centroid_id', right_on='centroid')

x = merged_data['centroid_lon']
y = merged_data['centroid_lat']
c_inacc = merged_data['inaccessibilite']
c_acc = merged_data['accessibilite']

x_diff = merged_data_0DRT['centroid_lon']
y_diff = merged_data_0DRT['centroid_lat']
print("merged_data_0DRT['inaccessibilite'] : ", merged_data_0DRT['inaccessibilite'])
print("merged_data['inaccessibilite'] : ", merged_data['inaccessibilite'])
#print("merged_data_0DRT['accessibilite'] : ", merged_data_0DRT['accessibilite'])
c_diff_inacc = merged_data_0DRT['inaccessibilite'] - merged_data['inaccessibilite']
c_diff_acc = merged_data_0DRT['accessibilite'] - merged_data['accessibilite']

################################################################################
#calcul inaccessibilité et accessibilité moyenne 
################################################################################

def moyenne(c, df):
    nb_centroids = df.shape[0]
    somme = c.sum()
    return somme/nb_centroids

################################################################################
# Tracer les graphiques : accessibilité et inaccessibilité
################################################################################
# Sélectionner les colonnes nécessaires pour tracer le graphique
def tracer_graph(mesure, x, y, c, df, show):
    '''
    mesure : 'Inaccessibilite' ou 'Accessibilite' ou 'Diff_Inaccessibilite' ou 'Diff_Accessibilite'
    df : res ou res_0DRT
    '''
    # Tracer les centroids suivant l'accessibilité ou l'inaccessibilité
    plt.scatter(x, y, c=c, alpha=0.5, marker='o', label="Centroids")
    plt.colorbar()  # Ajouter une légende pour la couleur
    plt.scatter(stops['stop_lon'], stops['stop_lat'], c='black', label = 'Stops', alpha = 0.5)

    if nb_DRT > 0 :
        plt.scatter(stops_filtered['stop_lon'], stops_filtered['stop_lat'], c='orange', label="Stop DRT")

    # Ajouter les étiquettes des points (stop_id) en gras et en rouge
    for i in range(len(stops_filtered)):
        plt.annotate(stops_filtered['stop_id'][i], xy=(stops_filtered['stop_lon'][i], stops_filtered['stop_lat'][i]), textcoords='offset points', xytext=(0,5), ha='center', fontweight='bold')
    
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.legend()

    moy = moyenne(c, df)

    plt.title('{} pour {}DRT \n Moyenne {} = {:.3e}'.format(mesure, nb_DRT, mesure, moy))
    path_save_fig = os.path.normpath("./Results_{}/Graph/{}_{}DRT.png".format(Data, mesure, nb_DRT))

    path_graph = os.path.normpath("./Results_{}/Graph".format(Data))
    if not os.path.exists(path_graph):
        os.mkdir(path_graph)
    
    plt.savefig(path_save_fig, format = 'png') 
    if show == True :
        plt.show()

################################################################################
# Graphs 
tracer_graph(mesure = 'Inaccessibilite', x = x, y = y, c = c_inacc, df = res, show = show)
tracer_graph(mesure = 'Accessibilite', x = x, y = y, c = c_acc,  df = res, show = show)
tracer_graph(mesure = 'Diff_Inaccessibilite', x = x_diff, y = y_diff, c = c_diff_inacc, df = res_0DRT, show = show)
tracer_graph(mesure = 'Diff_Accessibilite', x = x_diff, y = y_diff, c = c_diff_acc, df = res_0DRT, show = show)
################################################################################