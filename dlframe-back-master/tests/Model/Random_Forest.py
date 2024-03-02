import numpy as np
from collections import Counter
from sklearn.tree import DecisionTreeClassifier


class Random_Forest:
    def __init__(self, n_model=10):
        self.n_model = n_model
        self.models = []

    def fit(self, X_train, y_train):
        n = len(X_train)
        for i in range(self.n_model):
            random_indices = np.random.choice(n, n, replace=True)
            random_features = X_train[random_indices]
            random_labels = y_train[random_indices]
            model = DecisionTreeClassifier()
            model.fit(random_features, random_labels)
            self.models.append(model)

    def predict(self, X_test):
        predictions = []
        for x in X_test:
            votes = [model.predict([x])[0] for model in self.models]
            prediction = Counter(votes).most_common(1)[0][0]
            predictions.append(prediction)
        return predictions
