"""
  @project dlframe-back-master
  @Package 
  @author WeiJingqi
  @date 2023/11/12 - 14:54
 """
import numpy as np


class DecisionTree:     # 6.3
    def __init__(self, max_depth=float('inf'), min_samples_split=2, min_impurity_decrease=0.0):
        self.max_depth = max_depth  # 最大深度
        self.min_samples_split = min_samples_split  # 最小样本数
        self.min_impurity_decrease = min_impurity_decrease  # 最小不纯度减少值

    def calculate_gain(self, parent, left, right):
        return self.calculate_mse(parent) - (len(left) / len(parent)) * self.calculate_mse(left) \
            - (len(right) / len(parent)) * self.calculate_mse(right)

    def calculate_mse(self, labels):
        if len(labels) == 0:
            return 0
        mean_value = np.mean(labels)
        mse = np.mean((labels - mean_value) ** 2)
        return mse

    def fit(self, X, y, depth=0):
        if depth >= self.max_depth or len(set(y)) == 1:
            return np.mean(y)

        best_split_feature, best_split_value, best_gain = None, None, -np.inf
        best_left_indices, best_right_indices = None, None

        for feature in range(X.shape[1]):
            unique_values = np.unique(X[:, feature])
            for value in unique_values:
                left_indices = np.where(X[:, feature] <= value)[0]
                right_indices = np.where(X[:, feature] > value)[0]
                gain = self.calculate_gain(y, y[left_indices], y[right_indices])
                if gain > best_gain:
                    best_gain = gain
                    best_split_feature = feature
                    best_split_value = value
                    best_left_indices = left_indices
                    best_right_indices = right_indices

        if best_gain == 0:
            return np.mean(y)

        left_tree = self.fit(X[best_left_indices], y[best_left_indices], depth + 1)
        right_tree = self.fit(X[best_right_indices], y[best_right_indices], depth + 1)
        self.tree = {'feature': best_split_feature, 'value': best_split_value, 'left': left_tree, 'right': right_tree}
        return self.tree

    def predict_tree(self, X, tree):
        # 出现警告：predict_tree返回的如果是维数大于0的数组而不是一个标量可能会报错
        if isinstance(tree, np.float64):
            return np.full(len(X), tree)
        predictions = np.zeros(len(X))
        for i in range(len(X)):
            if X[i, tree['feature']] <= tree['value']:
                predictions[i] = self.predict_tree(X[i].reshape(1, -1), tree['left'])
            else:
                predictions[i] = self.predict_tree(X[i].reshape(1, -1), tree['right'])
        return predictions

    def predict(self, X):
        return self.predict_tree(X, self.tree)

