"""
  @project setup.py
  @Package 
  @author WeiJingqi
  @date 2024/1/30 - 20:32
 """
from sklearn.datasets import load_iris, load_wine
from sklearn.model_selection import train_test_split

from dlframe import Logger
from tests.Display import Dataset
from tests.Rewrite_main import NodeManager


def register(para1, para2="default"):  # para1:"dataset" ,para2: wine/iris
    def inner(class_name):  # 类名
        def wrapper(*args):  # 由类初始化传入manager
            manager = args[0]
            class_params = args[1:]
            # 先判断是否存在注册好的节点
            # 不存在：注册并添加当前的参数字典
            # 存在添加参数到已有节点的字典
            para_name = para2
            if para_name == "default":
                para_name = class_name.__name__
            if len(class_params) == 0:      # 要返回的对象，所需的字典也在对象内
                ret = class_name()
            else:
                ret = class_name(class_params)
                # if manager.registed_nodes[para1]:   # 已注册节点
            if para1 in manager.registed_nodes:  # 已注册节点
                registed_node = manager.registed_nodes[para1]  # 拿到已注册的节点


            else:  # 未注册，注册当前节点
                new_node = manager.create_node(para1, {para_name + str(class_params): ret})  # 产生的Node
                manager.registed_nodes[para1] = new_node  # 注册节点

            return ret

        return wrapper

    return inner  # 返回的还是类对象本身，而产生的Node用字典存起来，使用时候再返回


@register('dataset')
class Iris(Dataset):
    data_dict = None

    def __init__(self) -> None:
        super().__init__()
        iris = load_iris()
        self.data_dict = iris


@register('dataset', 'wine-test')  # 'Wine'的名称，默认是类名
# @register('dataset')  # 等价于manager.create_node('dataset', {'Wine': Wine, 'Iris': Iris})
class Wine(Dataset):  # 没有的话新建节点，有的话添加参数
    data_dict = None

    def __init__(self) -> None:
        super().__init__()
        wine = load_wine()
        self.data_dict = wine


@register('spliter')
class TestSplitter:
    def __init__(self, ratio=0.5) -> None:
        super().__init__()
        self.ratio = ratio
        self.logger = Logger.get_logger('TestSplitter')
        self.logger.print("I'm ratio:{}".format(self.ratio))

    # def set_params(self, ratio):
    #     self.ratio = ratio
    #     self.logger.print("I'm ratio:{}".format(self.ratio))
    #     print("spliter-set_params")

    def split(self, dataset):
        X, y = dataset['data'], dataset['target']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=self.ratio)
        return X_train, X_test, y_train, y_test


# dataset = manager.registed_nodes["dataset"]在此之后在进行类的初始化，而不是在一开始
# Data_Class = manager["dataset"]
# data_set = Data_Class()

if __name__ == '__main__':
    manager = NodeManager(if_parallel=False)
    Wine(manager)                   # 这样情况下 dataset内是类对象而不是所需要的数据集
    Iris(manager)
    TestSplitter(manager, 0.8)      # 出现问题，即出现了两个Spliter，应该是ratio0.5和ratio0.8                              0
    TestSplitter(manager, 0.5)      # 设置为名字 = 默认名字 + 参数
    print(0)

    # 数据集使用的是类之中获取到的数据集，而其他使用的是带参数的类本
