import pandas as pd

# Charger les données
df = pd.read_csv("Credit Data_Fichier Clients.csv")
TARGET = "bad_client_target"

# Détection automatique des variables catégorielles :
# - colonnes de type 'object'
# - colonnes numériques avec peu de valeurs uniques (par exemple ≤ 20)
cat_vars = list(df.select_dtypes(include=["object"]).columns)
low_card_num = [c for c in df.select_dtypes(include=["int64", "float64"]).columns 
                if c != TARGET and df[c].nunique() <= 20]
categorical_vars = cat_vars + low_card_num

print("Variables catégorielles détectées :", categorical_vars)

# Boucle sur chaque variable catégorielle
for var in categorical_vars:
    print(f"\n=== Taux de défaut par modalité pour '{var}' ===")
    taux_defaut = df.groupby(var)[TARGET].mean().sort_values(ascending=False)
    print(taux_defaut)
