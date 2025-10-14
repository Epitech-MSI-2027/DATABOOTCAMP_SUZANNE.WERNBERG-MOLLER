import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Chargement du fichier CSV
df = pd.read_csv("Credit Data_Fichier Clients.csv")

# 2. Liste des variables catégorielles à analyser
categorical_vars = ['sex', 'education', 'product_type', 'family_status']

# 3. Boucle sur chaque variable pour calculer et afficher les taux de défaut
for var in categorical_vars:
    print(f"\n=== Analyse de la variable : {var} ===")
    
    # Calcul des effectifs et taux de défaut
    grouped = df.groupby(var)['bad_client_target'].agg(['count', 'sum', 'mean']).reset_index()
    grouped.rename(columns={
        'count': 'Nombre_total',
        'sum': 'Mauvais_payeurs',
        'mean': 'Taux_de_defaut'
    }, inplace=True)
    
    print(grouped)
    
    # 4. Visualisation du taux de défaut par modalité
    plt.figure(figsize=(8, 4))
    sns.barplot(data=grouped, x=var, y='Taux_de_defaut', palette='viridis')
    plt.title(f"Taux de défaut par {var}")
    plt.ylabel("Taux de défaut")
    plt.xlabel(var)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
