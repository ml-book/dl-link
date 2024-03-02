from sklearn.metrics import accuracy_score, f1_score, r2_score, mean_absolute_error
from sklearn.model_selection import train_test_split

from dlframe import WebManager, Logger

from sklearn.datasets import load_wine, load_iris

import sklearn.svm as svm
from sklearn import tree


# def class_register(para1):
#     print(para1)
#     def inner(class_name):
#         print(class_name)
#         def wrapper(manager):
#             ret = class_name()
#             name = para1
#             dict = {ret}
#             new_node = manager.create_node(name, dict)  # 产生的Node
#             manager.registed_nodes[para1] = new_node
#             return ret
#         return wrapper
#     return inner  # 返回的还是类对象本身，而产生的Node用字典存起来，使用时候再返回


# 数据集
class Dataset:
    def __init__(self) -> None:
        super().__init__()
        # data_dict = {}
        #
        # wine = load_wine()
        # data_dict['wine'] = wine
        #
        # iris = load_iris()
        # data_dict['iris'] = iris
        #
        # boston_housing = tf.keras.datasets.boston_housing
        # data_dict['boston_housing'] = boston_housing
        # self.data_dict = data_dict
        self.logger = Logger.get_logger('Dataset')

    # def __len__(self) -> int:
    #     return len(self.data_dict)
    #
    # def __getitem__(self, name: str):
    #     return self.data_dict[name]


# @class_register("dataset")    # 对每个类进行装饰，是只注册一个dataset/iris节点只包含iris？？？该如何使用
class Iris(Dataset):
    data_dict = None

    def __init__(self) -> None:
        super().__init__()
        iris = load_iris()
        self.data_dict = iris
        self.args = {}

    def set_params(self, args):
        self.args = args
        print('--------------------set_args----------------------')
        print(args)

    def get_params(self):
        return self.args


class Wine(Dataset):
    data_dict = None

    def __init__(self) -> None:
        super().__init__()
        wine = load_wine()
        self.data_dict = wine
        self.args = {}

    def set_params(self, args):
        self.args = args
        print('--------------------set_args----------------------')
        print(args)
        # 储存args，参数是事先约定好的，然后设置参数或者方法调用时从args中选择

    def get_params(self):  # 在manager中实现获取到每个模型的get_params
        return self.args


class TrainTestDataset:
    def __init__(self, item) -> None:
        super().__init__()
        self.item = item

    def __len__(self) -> int:
        return len(self.item)

    def __getitem__(self, idx: int):
        return self.item[idx]


#

# 数据集切分器
class TestSplitter:
    def __init__(self, ratio=0.5) -> None:  # 1.29设置了一个默认值
        super().__init__()
        self.ratio = ratio
        self.logger = Logger.get_logger('TestSplitter')
        self.logger.print("I'm ratio:{}".format(self.ratio))
        self.args = {'ratio': {0.8, 0.5}}

    def set_params(self, args):
        self.args = args
        print('--------------------set_args----------------------')
        print(args)
        # 储存args，参数是事先约定好的，然后设置参数或者方法调用时从args中选择

    def get_params(self):  # 在manager中实现获取到每个模型的get_params
        return self.args

    # def set_params(self, ratio):
    #     self.ratio = ratio
    #     self.logger.print("I'm ratio:{}".format(self.ratio))
    #     print("spliter-set_params")

    def split(self, dataset):
        X, y = dataset['data'], dataset['target']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=self.ratio)
        return X_train, X_test, y_train, y_test


# 模型
class TestModel:
    def __init__(self, learning_rate, model_name: str, model_class: int) -> None:
        """
        根据数据集判别是分类还是回归,
        @param learning_rate:
        @param model_name:
        """
        super().__init__()
        self.model_class = model_class  # 0是分类， 1是回归
        if model_name == 'svm':
            if self.model_class == 0:
                self.model = svm.SVC(kernel='rbf', C=1)  # svm用于分类
            else:
                self.model = svm.SVR(kernel='linear')  # svc用于回归
        if model_name == 'tree':
            self.model = tree.DecisionTreeClassifier()
        self.learning_rate = learning_rate
        self.logger = Logger.get_logger('TestModel')

    def train(self, trainDataset, targetDataset) -> None:
        self.logger.print("trainging, lr = {}, trainDataset = {}".format(self.learning_rate, trainDataset))
        # print(f'train execute-------------------------------------------:')
        self.model.fit(trainDataset, targetDataset)

    def test(self, testDataset):
        self.logger.print("testing")
        y_pred = self.model.predict(testDataset)
        return y_pred


# 结果判别器
class TestJudger:
    def __init__(self, model_class=0) -> None:
        # 通过名字分辨所需的评价指标：可以预先设定一个字典
        self.evaluation_dict = [  # 分类或回归任务所需的评价指标
            ['Accuracy', 'F1'],
            ['R²', 'MAE']
        ]
        self.eva_list = self.evaluation_dict[model_class]
        super().__init__()
        self.logger = Logger.get_logger('TestJudger')
        self.args = {'model_class': {0, 1}}

    def set_params(self, args):
        self.args = args
        print('--------------------set_args----------------------')
        print(args)
        # 储存args，参数是事先约定好的，然后设置参数或者方法调用时从args中选择

    def get_params(self):  # 在manager中实现获取到每个模型的get_params
        return self.args

    def judge(self, test_true, y_predict) -> None:
        """
        可以分为分类任务或者回归任务的评价指标：
        分类任务的常用评价指标：准确率（Accuracy）、精确率（Precision）、召回率（Recall）、P-R曲线（Precision-Recall Curve）、F1 Score、混淆矩阵（Confuse Matrix）、ROC、AUC。
        回归任务的常用评价指标：R²、MAE、MSE
        分类任务若是无监督可能没有test_true
        @param test_true: 验证集的真实标签
        @param y_predict: 验证集的预测值
        @return:
        """
        # 在二元分类时候对参数做处理
        # if model
        test_true = [1 if label == 0 else 0 for label in test_true]
        y_predict = [1 if label == 0 else 0 for label in y_predict]

        self.logger.print("y_predict = {}".format([y_predict[i] for i in range(len(y_predict))]))
        self.logger.print("real_value = {}".format([test_true[i] for i in range(len(test_true))]))

        for eva in self.eva_list:
            if eva == 'Accuracy':
                accuracy = accuracy_score(test_true, y_predict)
                print(f'accuracy: {accuracy}')
            elif eva == 'F1':
                f1 = f1_score(test_true, y_predict, average='weighted')
                print(f'f1-score: {f1}')
            elif eva == 'R²':
                r2 = r2_score(test_true, y_predict)
                print(f'R²: {r2}')
            elif eva == 'MAE':
                mae = mean_absolute_error(test_true, y_predict)
                print(f'MAE: {mae}')


class Judger_Clf:
    def __init__(self) -> None:
        # 通过名字分辨所需的评价指标：可以预先设定一个字典
        self.evaluation_dict = ['Accuracy', 'F1']  # 分类任务评价指标
        super().__init__()
        self.logger = Logger.get_logger('Judger-clf')
        self.args = {}

    def set_params(self, args):
        self.args = args
        print('--------------------set_args----------------------')
        print(args)
        # 储存args，参数是事先约定好的，然后设置参数或者方法调用时从args中选择

    def get_params(self):  # 在manager中实现获取到每个模型的get_params
        return self.args

    def judge(self, test_true, y_predict) -> None:
        """
        可以分为分类任务或者回归任务的评价指标：
        分类任务的常用评价指标：准确率（Accuracy）、精确率（Precision）、召回率（Recall）、P-R曲线（Precision-Recall Curve）、F1 Score、混淆矩阵（Confuse Matrix）、ROC、AUC。
        回归任务的常用评价指标：R²、MAE、MSE
        分类任务若是无监督可能没有test_true
        @param test_true: 验证集的真实标签
        @param y_predict: 验证集的预测值
        @return:
        """
        # 在二元分类时候对参数做处理
        # if model
        test_true = [1 if label == 0 else 0 for label in test_true]
        y_predict = [1 if label == 0 else 0 for label in y_predict]

        self.logger.print("y_predict = {}".format([y_predict[i] for i in range(len(y_predict))]))
        self.logger.print("real_value = {}".format([test_true[i] for i in range(len(test_true))]))

        for eva in self.evaluation_dict:
            if eva == 'Accuracy':
                accuracy = accuracy_score(test_true, y_predict)
                print(f'accuracy: {accuracy}')
            elif eva == 'F1':
                f1 = f1_score(test_true, y_predict, average='weighted')
                print(f'f1-score: {f1}')
            elif eva == 'R²':
                r2 = r2_score(test_true, y_predict)
                print(f'R²: {r2}')
            elif eva == 'MAE':
                mae = mean_absolute_error(test_true, y_predict)
                print(f'MAE: {mae}')


class Judger_Rlf:
    def __init__(self) -> None:
        # 通过名字分辨所需的评价指标：可以预先设定一个字典
        self.evaluation_dict = ['R²', 'MAE']  # 回归任务评价指标
        super().__init__()
        self.logger = Logger.get_logger('Judger-rlf')
        self.args = {}

    def set_params(self, args):
        self.args = args
        print('--------------------set_args----------------------')
        print(args)
        # 储存args，参数是事先约定好的，然后设置参数或者方法调用时从args中选择

    def get_params(self):  # 在manager中实现获取到每个模型的get_params
        return self.args

    def judge(self, test_true, y_predict) -> None:
        """
        可以分为分类任务或者回归任务的评价指标：
        分类任务的常用评价指标：准确率（Accuracy）、精确率（Precision）、召回率（Recall）、P-R曲线（Precision-Recall Curve）、F1 Score、混淆矩阵（Confuse Matrix）、ROC、AUC。
        回归任务的常用评价指标：R²、MAE、MSE
        分类任务若是无监督可能没有test_true
        @param test_true: 验证集的真实标签
        @param y_predict: 验证集的预测值
        @return:
        """
        # 在二元分类时候对参数做处理
        # if model
        test_true = [1 if label == 0 else 0 for label in test_true]
        y_predict = [1 if label == 0 else 0 for label in y_predict]

        self.logger.print("y_predict = {}".format([y_predict[i] for i in range(len(y_predict))]))
        self.logger.print("real_value = {}".format([test_true[i] for i in range(len(test_true))]))

        for eva in self.evaluation_dict:
            if eva == 'Accuracy':
                accuracy = accuracy_score(test_true, y_predict)
                print(f'accuracy: {accuracy}')
            elif eva == 'F1':
                f1 = f1_score(test_true, y_predict, average='weighted')
                print(f'f1-score: {f1}')
            elif eva == 'R²':
                r2 = r2_score(test_true, y_predict)
                print(f'R²: {r2}')
            elif eva == 'MAE':
                mae = mean_absolute_error(test_true, y_predict)
                print(f'MAE: {mae}')
