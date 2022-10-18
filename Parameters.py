# Parametres

## Intervenant dans le fichier 'Reduce_Centroid_Stop.py' :
rayon_exclusif = 6500 # supprime les centroides n'ayant aucune station situee dans ce rayon
rayon_walk = 1000 # cree une relation WALK entre un centroide et les stations situees dans ce rayon
departure_time = "'08:30:00'" # horaire de depart pour tous les centroides
vitesse_walk = 3 # en km/h, vitesse moyenne de marche

## Intervenant dans le fichier 'Change_departure_time_centroid.py' :
new_departure_time = "'08:30:00'" # type String, nouvel horaire de départ pour tous les centroïdes

## Intervenant dans le fichier 'Load_DRT.py' :
h0 = [60, 120, 240, 960, 1920, 3840] # valeurs de h possibles (proposées)
idx_h = 0 # intervient également dans le fichier 'Res_DataFrames.py' plus bas
h = h0[idx_h] # valeur de h actuelle

densite = 26 # 26 pax/h/km^2, nombre de passagers par km² par heure
longueur = 4000 # en metres, longeur de la zone de service DRT (rectangulaire)
largeur = 2000 # en metres, largeur de la zone de service DRT (rectangulaire)
vitesse_DRT = 30 # en km/h, vitesse moyenne des vehicules DRT

liste_stations_DRT = [124,2612,2568,2635,384,411,739,467,2503,509,830,590,629,178,2601,661,257,807,92,2459]
# liste des stop_id des stations DRT


## Intervenant dans le fichier 'PCC_totaltimes_DataFrames.py' :
ray_max = 10000 # en metres, rayon max auquel doivent appartenir les stations pour etre une destination du centroide
ray_min = 2000 # en metres, rayon min auquel doivent appartenir les stations pour etre une destination du centroide


## Intervenant dans 'Res_DataFrames.py' :
h0_str = ['1_min', '2_min', '4_min', '16_min', '32_min', '64_min'] # format String pour le nom des fichiers
# idx_h = 0
h_str = h0_str[idx_h] # valeur de h actuelle
