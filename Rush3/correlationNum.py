# 1. Import des bibliothèques nécessaires
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 2. Chargement du fichier CSV
df = pd.read_csv("Credit Data_Fichier Clients.csv")

# 3. Afficher les premières lignes pour vérifier la structure
print("Aperçu des données :")
print(df.head())

# 4. Sélection des variables numériques pour la corrélation
# On exclut les colonnes catégorielles (texte)
numeric_cols = df.select_dtypes(include=['int64', 'float64'])

print("\nVariables numériques utilisées pour la corrélation :")
print(numeric_cols.columns)

# 5. Calcul de la matrice de corrélation
corr_matrix = numeric_cols.corr()

print("\nMatrice de corrélation :")
print(corr_matrix)

# 6. Visualisation de la matrice de corrélation sous forme de heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Matrice de corrélation entre variables numériques")
plt.show()

# 7. Corrélation avec la variable cible (bad_client_target)
target_corr = corr_matrix['bad_client_target'].sort_values(ascending=False)

print("\nCorrélation de chaque variable avec la cible (bad_client_target) :")
print(target_corr)

# 8. Visualisation simple des corrélations avec la cible
plt.figure(figsize=(8, 5))
sns.barplot(x=target_corr.index, y=target_corr.values, palette="viridis")
plt.xticks(rotation=45)
plt.title("Corrélation avec la variable cible (bad_client_target)")
plt.ylabel("Coefficient de corrélation")
plt.xlabel("Variable")
plt.show()
