import os
import stat
import Parameters

'''
Excecuter ce fichier avec sudo si problèmes de permissions 
'''

Data = Parameters.Data

directory_path = "Results_{}".format(Data)

# Parcourir tous les fichiers du répertoire
for root, dirs, files in os.walk(directory_path):
    for file_name in files:
        file_path = os.path.join(root, file_name)

        # Obtenir les permissions actuelles du fichier
        current_permissions = stat.S_IMODE(os.lstat(file_path).st_mode)

        # Ajouter les permissions de lecture, écriture et exécution pour tous les utilisateurs
        new_permissions = current_permissions | stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO

        # Changer les permissions du fichier
        os.chmod(file_path, new_permissions)

print("Les permissions de tous les fichiers du répertoire ont été modifiées avec succès.")

