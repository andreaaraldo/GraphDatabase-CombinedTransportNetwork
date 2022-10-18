# Parametres

## Intervenant dans le fichier 'Reduce_Centroid_Stop.py' :
rayon_exclusif = 6500 # supprime les centroides n'ayant aucune station situee dans ce rayon
rayon_walk = 1000 # cree une relation WALK entre un centroide et les stations situees dans ce rayon
departure_time = "'08:30:00'" # horaire de depart pour tous les centroides
vitesse_walk = 3 # en km/h, vitesse moyenne de marche

## Intervenant dans le fichier 'Change_departure_time_centroid.py' :
new_departure_time = "'08:30:00'" # type String

## Intervenant dans le fichier 'Load_DRT.py' :
h0 = [60, 120, 240, 960, 1920, 3840]
densite = 26 # 26 pax/h/km^2 
longueur = 4000 # en metres
largeur = 2000 # en metres
v = 30 # en km/h, vitesse moyenne des vehicules DRT

h = h0[0]

liste_stations_DRT = [124, 123]


## Intervenant dans le fichier 'PCC_totaltimes_DataFrames.py' :
ray_max = 10000 # en metres, rayon max auquel doivent appartenir les stations pour etre une destination du centroide
ray_min = 2000 # en metres, rayon min auquel doivent appartenir les stations pour etre une destination du centroide
