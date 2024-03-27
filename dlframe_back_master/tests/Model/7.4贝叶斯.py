"""
  @project dlframe-back-master
  @Package 
  @author WeiJingqi
  @date 2023/11/12 - 15:33
 """
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from sklearn.naive_bayes import GaussianNB
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

# 没有模型，只有使用示例

mpl.rcParams['font.sans-serif'] = [u'simHei']
mpl.rcParams['axes.unicode_minus'] = False

data = load_iris().data[:, 2:4]
y = load_iris().target
x_train, x_test, y_train, y_test = train_test_split(data, y, random_state=1)
model = GaussianNB().fit(x_train, y_train)
pre_y = model.predict(x_test)

# 准确率
m = 0
for i in range(len(pre_y)):
    if pre_y[i] == y_test[i]:
        m = m + 1
print("准确率：", m * 1.0 / len(pre_y))

# 绘图
# 生成格点
N, M = 250, 250  # 横纵各采样多少个值
x1_min, x1_max = data[:, 0].min(), data[:, 0].max()  # 第0列的范围
y2_min, y2_max = data[:, 1].min(), data[:, 1].max()  # 第1列的范围
t1 = np.linspace(x1_min, x1_max, N)
t2 = np.linspace(y2_min, y2_max, M)
x1, x2 = np.meshgrid(t1, t2)  # 生成网格采样点
x_test = np.stack((x1.flat, x2.flat), axis=1)  # 测试点

y_test = model.predict(x_test)

# 绘制格点预测数据
plt.scatter(x_test[y_test == 0][:, 0], x_test[y_test == 0][:, 1], color='#77E0A0')
plt.scatter(x_test[y_test == 1][:, 0], x_test[y_test == 1][:, 1], color='#FF8080')
plt.scatter(x_test[y_test == 2][:, 0], x_test[y_test == 2][:, 1], color='#A0A0FF')

# 绘制原始数据
plt.scatter(data[y == 0][:, 0], data[y == 0][:, 1], marker="*", label=u'第一类')
plt.scatter(data[y == 1][:, 0], data[y == 1][:, 1], marker="v", label=u'第二类')
plt.scatter(data[y == 2][:, 0], data[y == 2][:, 1], marker="o", label=u'第三类')

plt.xlabel(u'花瓣长度', fontsize=14)
plt.ylabel(u'花瓣宽度', fontsize=14)
plt.xlim(x1_min, x1_max)
plt.ylim(y2_min, y2_max)
plt.legend(loc="upper left")
plt.show()
