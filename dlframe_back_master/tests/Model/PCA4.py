"""
  @project dlframe-back-master
  @Package 
  @author WeiJingqi
  @date 2023/11/13 - 8:16
 """

import numpy as np
import pandas as pd
from sklearn.datasets import load_iris
import matplotlib.pyplot as plt


# 定义PCA方法
class Pca:

    def __init__(self, df):
        self.df = df
        self.data_mat = df.iloc[:, :-1].values

    def fit(self, data_mat):
        # 求平均值
        mean_val = np.mean(data_mat, axis=0)
        # 去中心化
        mean_removed = data_mat - mean_val
        # 获取协方差矩阵
        cov_mat = np.cov(mean_removed, rowvar=0)
        # 获取特征根及特征向量
        eigen_vals, eigen_vecs = np.linalg.eig(cov_mat)
        # 特征根排序
        eigen_val_ind = np.argsort(eigen_vals)[::-1]
        eigen_vals = eigen_vals[eigen_val_ind]
        eigen_vecs = eigen_vecs[:, eigen_val_ind]

        # 计算累计解释方差比例
        total_variance = np.sum(eigen_vals)
        var_exp_ratio = eigen_vals / total_variance
        cum_var_exp_ratio = np.cumsum(var_exp_ratio)

        # 根据累计解释方差比例选择最优维数
        num_feat = np.sum(cum_var_exp_ratio >= 0.95)

        # 选择满足阈值要求的特征向量
        red_eigen_vecs = eigen_vecs[:, :num_feat]
        # 新维度的数据
        low_data_mat = mean_removed.dot(red_eigen_vecs)
        # 获取重构数据
        return low_data_mat

    def res(self):
        low_data_mat = self.fit(self.data_mat)
        print(low_data_mat)
        df = pd.DataFrame(low_data_mat)
        df['target'] = self.df.iloc[:, -1]
        return df


# 主函数调用
if __name__ == '__main__':
    # 导入鸢尾花数据集
    iris = load_iris()
    # 获取特征数据
    df = pd.DataFrame(iris.data, columns=iris.feature_names)

    # 进行PCA降维，根据累计解释方差比例自动选择最优维数
    pca = Pca(df)
    result_df = pca.res()

    # 获取降维后的数据和标签
    low_data_mat = result_df.iloc[:, :-1].values
    target = result_df['target']

    # 创建散点图
    plt.scatter(low_data_mat[:, 0], low_data_mat[:, 1], c=target)
    plt.xlabel('Principal Component 1')
    plt.ylabel('Principal Component 2')
    plt.title('PCA - Iris Dataset')

    # 显示图像
    plt.show()
