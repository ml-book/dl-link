"""
  @project setup.py
  @Package 
  @author WeiJingqi
  @date 2023/11/27 - 17:02
  代码装饰器
 """
from tests.Model.DecisionTree import DecisionTree
from tests.Model.KNN import KNN
from tests.Model.K_Means import K_Means
from tests.Model.LinearLogisticRegression import LinearLogisticRegression
from tests.Model.LinearRegression import LinearRegression
from tests.Model.Random_Forest import Random_Forest
from tests.Model.svm import SVM
from tests.Rewrite import NodeManager
from tests.Display import *


# 对每个类进行装饰器注册！1.9日
# function：对类进行初始化，返回类对象，但是添加注册好的节点到字典中 1.16 ！！！


def register(para1, para2="default"):  # para1:name ,para2: 想要的那个对象
    def inner(class_name):
        def wrapper(manager):
            ret = class_name(para1)
            name = ret.name
            if para2 == "default":
                dict = ret.dict  # 完整的字典
            else:
                dict = {para2: ret.dict[para2]}  # 只在字典中保留想要的那个
            new_node = manager.create_node(name, dict)  # 产生的Node
            manager.registed_nodes[para1] = new_node
            return ret

        return wrapper

    return inner  # 返回的还是类对象本身，而产生的Node用字典存起来，使用时候再返回


# manager写一个getInstance单例模式保证manager统一，然后装饰器用manager.register调用
# dataset, iris 两个参数，IRIS是可以省略的，若是省略以DatasetDict作第二个参数，即字典作为参数???
@register("dataset")  # 没有第二个参数的情况下
# @register("dataset", "iris")  # 第二个参数是IRIS的情况下
class DatasetDict:
    dict = []
    name = None

    def __init__(self, name) -> None:
        self.dict = {'iris': Iris().data_dict,
                     'wine': Wine().data_dict}
        self.name = name


@register("data_split")
class SplitDict:
    dict = []
    name = None

    def __init__(self, name) -> None:
        self.dict = {'ratio:0.8': TestSplitter(0.8),
                     'ratio:0.5': TestSplitter(0.5)}
        self.name = name


@register("model")  # 在这里加一个model需要的args（用一个字典存放，需要发给前端）
class ModelDict:
    dict = []
    name = None

    def __init__(self, name) -> None:
        self.dict = {'LinearRegression': LinearRegression(),
                     'DecisionTree': DecisionTree(),
                     'LinearLogisticRegression': LinearLogisticRegression(),
                     'KNN': KNN(),
                     'svm': SVM(),
                     'RandomForest': Random_Forest(),
                     'k-means': K_Means()}
        self.name = name


@register("judger")
class JudgeDict:
    dict = []
    name = None

    def __init__(self, name) -> None:
        self.dict = {'judge_clf': Judger_Clf(),
                     'judge_rlf': Judger_Rlf()}
        self.name = name


if __name__ == '__main__':
    manager = NodeManager()
    dataset = DatasetDict(manager)
    # dataset = manager["dataset"]    # 来调用出注册好的节点get_item
    spliter = SplitDict(manager)
    model = ModelDict(manager)
    judger = JudgeDict(manager)
    print(dataset)
    print(manager.registed_nodes["dataset"])
    print(manager.registed_nodes)
