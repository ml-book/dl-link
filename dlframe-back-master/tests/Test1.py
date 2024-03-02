"""
  @project setup.py
  @Package 
  @author WeiJingqi
  @date 2023/11/19 - 14:17
 """
import numpy as np

# 定义RBF核函数
def rbf_kernel(x1, x2, gamma):
    return np.exp(-gamma * np.linalg.norm(x1 - x2) ** 2)

# 定义SVM训练函数
def svm_train(X, y, gamma, C, num_epochs, learning_rate):
    num_samples, num_features = X.shape
    alpha = np.zeros(num_samples)
    bias = 0

    for epoch in range(num_epochs):
        for i in range(num_samples):
            error = 0
            for j in range(num_samples):
                error += alpha[j] * y[j] * rbf_kernel(X[i], X[j], gamma)
            error += bias
            if (y[i] * error) < 1:
                alpha[i] += learning_rate
                bias += learning_rate * y[i]

    return alpha, bias

# 定义SVM预测函数
def svm_predict(X_test, X_train, y_train, alpha, bias, gamma):
    num_samples_test = X_test.shape[0]
    num_samples_train = X_train.shape[0]
    y_pred = np.zeros(num_samples_test)

    for i in range(num_samples_test):
        pred = 0
        for j in range(num_samples_train):
            pred += alpha[j] * y_train[j] * rbf_kernel(X_test[i], X_train[j], gamma)
        pred += bias
        y_pred[i] = np.sign(pred)

    return y_pred

# 读取鸢尾花数据集
def load_iris_data():
    from sklearn.datasets import load_iris
    iris = load_iris()
    X = iris.data
    y = iris.target
    return X, y

# 数据预处理
def preprocess_data(X):
    X_normalized = (X - np.mean(X, axis=0)) / np.std(X, axis=0)
    return X_normalized

# 划分训练集和测试集
def train_test_split(X, y, test_ratio=0.2):
    num_samples = X.shape[0]
    num_test_samples = int(num_samples * test_ratio)

    # 随机打乱数据集
    shuffled_indices = np.random.permutation(num_samples)
    X_shuffled = X[shuffled_indices]
    y_shuffled = y[shuffled_indices]

    X_test = X_shuffled[:num_test_samples]
    y_test = y_shuffled[:num_test_samples]
    X_train = X_shuffled[num_test_samples:]
    y_train = y_shuffled[num_test_samples:]

    return X_train, y_train, X_test, y_test

# 主函数
def main():
    # 加载鸢尾花数据集
    X, y = load_iris_data()
    X = preprocess_data(X)

    # 划分训练集和测试集
    X_train, y_train, X_test, y_test = train_test_split(X, y, test_ratio=0.2)

    # 超参数设置
    gamma = 0.1
    C = 1.0
    num_epochs = 100
    learning_rate = 0.01

    # 训练SVM模型
    alpha, bias = svm_train(X_train, y_train, gamma, C, num_epochs, learning_rate)

    # 对测试集进行预测
    y_pred = svm_predict(X_test, X_train, y_train, alpha, bias, gamma)

    # 计算分类准确率
    accuracy = np.sum(y_pred == y_test) / len(y_test)
    print("Accuracy:", accuracy)

if __name__ == "__main__":
    main()
