import pandas as pd
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier
import numpy as np

x = pd.read_excel('Rush3.xlsx',usecols=['credit_amount']).to_numpy()
y = pd.read_excel('Rush3.xlsx',usecols=['income']).to_numpy()
classes = pd.read_excel('Rush3.xlsx',usecols=['bad_client_target']).to_numpy()

datax = np.array(x).flatten()
datay = np.array(y).flatten()
dataclasses = np.array(classes).flatten()

data = list(zip(datax, datay))
knn = KNeighborsClassifier(n_neighbors=5)

knn.fit(data, dataclasses)

plt.scatter(datax, datay, c=dataclasses)
plt.show()
