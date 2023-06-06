import subprocess
import os

for i in range(30):
    i = str(i)
    print("##########################\n \n Executing Heuristic.py... \n \n##########################")
    # Exécuter le fichier
    subprocess.run(['python3', 'Heuristic.py', i], check=True)