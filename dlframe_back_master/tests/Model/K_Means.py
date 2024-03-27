"""
  @project dlframe-back-master
  @Package 
  @author WeiJingqi
  @date 2023/11/12 - 20:40
 """
import random
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split


class K_Means:
    # 计算两点之间的距离
    def __init__(self):
        self.centroids = None

    def cal_distance(self, node1, node2):
        # 计算两个向量之间的欧式距离
        return np.sqrt(np.sum(np.square(node1 - node2)))

    # 初始化聚类中心
    def init_k_node(self, data, k):
        data = list(data)
        return random.sample(data, k)

    # 讲各节点分配给聚类中心
    def get_clusters(self, data, k_centroids):
        cluster_dict = dict()  # 用来存储每个类别对应的节点信息
        k = len(k_centroids)  # 可获取设定的聚类个数
        for node in data:
            cluster_idx = -1  # 设定初始类别为-1
            min_dis = float("inf")  # 设定初始聚类中心
            for idx in range(k):  # 计算节点同每个初始聚类中心的距离
                centroid = k_centroids[idx]
                distance = self.cal_distance(node, centroid)
                if distance < min_dis:
                    min_dis = distance
                    cluster_idx = idx
            # 存储每个类别包含的样本
            if cluster_idx not in cluster_dict.keys():
                cluster_dict[cluster_idx] = []
            cluster_dict[cluster_idx].append(node)
        return cluster_dict

    # 重新计算聚类中心
    def get_centroids(self, cluster_dict):
        new_k_centroids = []
        for cluster_idx in cluster_dict.keys():
            new_centroid = np.mean(cluster_dict[cluster_idx], axis=0)  # 每个类别中的均值
            new_k_centroids.append(new_centroid)
        return new_k_centroids

    # 计算各类间方差
    def get_variance(self, centroids, cluster_dict):
        sum = 0.0  # 初始化均方误差为0
        for cluster_idx in cluster_dict.keys():
            centroid = centroids[cluster_idx]  # 获取聚类中心
            distance = 0.0
            for node in cluster_dict[cluster_idx]:
                distance += self.cal_distance(node, centroid)
            sum += distance
        return sum

    # 进行最终聚类
    def fit(self, X_train, y_train):    # 无监督算法，不需要y_train，这该怎么办？
        data = X_train
        centroids = self.init_k_node(data, 3)  # 获取初始聚类中心
        cluster_dict = self.get_clusters(data, centroids)  # 初始分类
        new_var = self.get_variance(centroids, cluster_dict)  # 计算初始聚类均方差
        old_var = 1

        # 设定条件，当两次聚类得误差小于某个值时，说明聚类基本稳定：
        while abs(new_var - old_var) >= 0.00001:
            centroids = self.get_centroids(cluster_dict)  # 重新计算聚类中心
            cluster_dict = self.get_clusters(data, centroids)  # 再分类
            old_var = new_var
            new_var = self.get_variance(centroids, cluster_dict)  # 计算当前聚类均方差
        # print(centroids)
        self.centroids = centroids

    def predict(self, X_test):
        predicted_labels = []
        for node in X_test:
            min_distance = float('inf')
            predicted_label = None
            for i, centroid in enumerate(self.centroids):  # 找到当前node属于哪个center（i）
                distance = self.cal_distance(node, centroid)
                if distance < min_distance:
                    min_distance = distance
                    predicted_label = i
            predicted_labels.append(predicted_label)
        return predicted_labels
        # print(y_test)
        # accuracy = sum(1 for true, pred in zip(y_test, predicted_labels) if true == pred) / len(y_test)
        # print("准确率:", accuracy)

# if __name__ == '__main__':
#     dataset = load_iris()
#     X, y = dataset['data'], dataset['target']
#     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1)
#     centroids = fit(X_train)
#     predict(X_test, centroids, y_test)
