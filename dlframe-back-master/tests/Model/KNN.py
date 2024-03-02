import numpy as np
from collections import Counter

from sklearn.datasets import load_iris
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split


class KNN:

    def __init__(self) -> None:
        self.X_train = None
        self.y_train = None

    def euclidean_distance(self, x1, x2):  # 欧式距离计算函数
        return np.sqrt(np.sum((x1 - x2) ** 2))

    def fit(self, X_train, y_train):
        self.X_train = X_train
        self.y_train = y_train

    # KNN算法函数
    def predict_one(self, X, y, query_point, k=3):
        distances = []

        # 计算查询点与每个训练样本之间的距离
        for i in range(len(X)):
            distance = self.euclidean_distance(query_point, X[i])
            distances.append((distance, y[i]))

        # 根据距离从小到大排序
        distances = sorted(distances, key=lambda x: x[0])

        # 选取距离最小的K个样本
        k_nearest_neighbors = distances[:k]

        # 统计K个样本中各类别出现的次数
        class_counts = Counter([neighbor[1] for neighbor in k_nearest_neighbors])

        # 返回出现次数最多的类别作为预测结果
        most_common = class_counts.most_common(1)
        return most_common[0][0]

    def predict(self, X_test):
        y_predict = []
        for x in X_test:
            y_predict.append(self.predict_one(self.X_train, self.y_train, x, k=3))
        return y_predict



# # 加载鸢尾花数据集
# iris = load_iris()
# X, y = iris.data, iris.target
# model = KNN()
#
# # 划分训练集和测试集
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
#
# # 对测试集进行预测
# model.fit(X_train, y_train)
# y_pred = model.predict(X_test)
#
#
# # 计算准确率
# accuracy = accuracy_score(y_test, y_pred)
# print("准确率:", accuracy)