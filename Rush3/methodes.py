from tkinter import *
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.neighbors import KNeighborsClassifier
import numpy as np

# --- Chargement unique du fichier CSV ---
df = pd.read_csv('Credit Data_Fichier Clients.csv')

root = Tk()
root.title("Prédiction Crédit")
root.geometry("400x200")

Label(root, text="Méthode de prédiction").grid(row=0, column=0, padx=10, pady=5)
method_var = StringVar(value="regre_linear")
Radiobutton(root, text="Régression linéaire", variable=method_var, value="regre_linear").grid(row=0, column=1)
Radiobutton(root, text="Méthode KNN", variable=method_var, value="knn").grid(row=0, column=2)

Label(root, text="Abscisse client (credit_amount)").grid(row=1, column=0, padx=10, pady=5)
abs_entry = Entry(root)
abs_entry.grid(row=1, column=1, padx=10, pady=5)

Label(root, text="Ordonnée client (income)").grid(row=2, column=0, padx=10, pady=5)
ord_entry = Entry(root)
ord_entry.grid(row=2, column=1, padx=10, pady=5)

Label(root, text="Nombre k").grid(row=3, column=0, padx=10, pady=5)
nbk_entry = Entry(root)
nbk_entry.grid(row=3, column=1, padx=10, pady=5)

def submit_form():
    if method_var.get() == "regre_linear":
        # Lecture des variables nécessaires
        x = df['credit_amount'].to_numpy()
        y = df['income'].to_numpy()

        slope, intercept, r, p, std_err = stats.linregress(x, y)

        def myfunc(val):
            return slope * val + intercept

        # Nouveau point
        new_x = int(abs_entry.get())
        new_y = myfunc(new_x)

        # Affichage
        plt.scatter(x, y)
        plt.scatter(new_x, new_y, color='red', label=f"Nouveau point ({new_x},{int(new_y)})")
        plt.plot(x, list(map(myfunc, x)), color='orange')
        plt.xlabel("credit_amount")
        plt.ylabel("income")
        plt.legend()
        plt.show()

    elif method_var.get() == "knn":
        x = df['credit_amount'].to_numpy().flatten()
        y = df['income'].to_numpy().flatten()
        classes = df['bad_client_target'].to_numpy().flatten()

        data = list(zip(x, y))
        k = int(nbk_entry.get())
        knn = KNeighborsClassifier(n_neighbors=k)
        knn.fit(data, classes)

        new_x = int(abs_entry.get())
        new_y = int(ord_entry.get())
        new_point = [(new_x, new_y)]

        prediction = knn.predict(new_point)

        plt.scatter(x, y, c=classes, cmap='coolwarm', alpha=0.6)
        plt.scatter(new_x, new_y, c='green', edgecolors='black', s=100, label=f"Classe prédite: {prediction[0]}")
        plt.xlabel("credit_amount")
        plt.ylabel("income")
        plt.legend()
        plt.show()

    else:
        print("Erreur dans la sélection")


Button(root, text="Submit", command=submit_form).grid(row=4, columnspan=2, pady=20)

root.mainloop()
