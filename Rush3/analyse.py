import pandas as pd

# 1. Chargement du fichier
df = pd.read_csv('Credit Data_Fichier Clients.csv')

# 2. Analyse de la structure
print(df.info())            # types de données et valeurs manquantes
print(df.describe())        # statistiques descriptives des numériques
print(df.describe(include='all'))  # inclut aussi les colonnes catégorielles

# 3. Statistiques complémentaires
print(df['sex'].value_counts())
print(df['education'].value_counts())
print(df['product_type'].value_counts())
print(df['family_status'].value_counts())

# 4. Vérification de la distribution de la variable cible
print(df['bad_client_target'].value_counts(normalize=True))
