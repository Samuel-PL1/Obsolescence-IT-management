
import pandas as pd

data = {
    'Salle': ['Siège Paris - Bureau 101', 'Agence Lyon - Salle 205'],
    'Nom PC': ['PC-TEST-001', 'SRV-TEST-001'],
    'Description (Alias)': ['Poste de travail de test', 'Serveur de test'],
    'Système d\'exploitation PC': ['Windows 10 Pro', 'Ubuntu 20.04 LTS'],
    'Application': ['Microsoft Office', 'MySQL'],
    'Version': ['2019', '8.0'],
    'Fournisseur matériel': ['Dell', 'HP']
}

df = pd.DataFrame(data)

df.to_excel('test_import.xlsx', index=False)
print('Fichier test_import.xlsx créé.')

