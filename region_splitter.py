import pandas as pd
import numpy as np
import sklearn.model_selection
import sklearn.neighbors
import sklearn.preprocessing
class Region_finder:
    def __init__(self,towns,coordinates):
        self.data = towns[["Latitude","Longitude"]]
        self.labels = towns[["Kraj"]]
        self.test_data = coordinates[["y","x"]].rename(columns = {'y':'Latitude', 'x':'Longitude'})
    def predict_regions(self):
        estimator = sklearn.neighbors.KNeighborsClassifier(n_neighbors=1)
        estimator.fit(self.data,self.labels.values.ravel())
        prediction = estimator.predict(self.test_data)
        return prediction






