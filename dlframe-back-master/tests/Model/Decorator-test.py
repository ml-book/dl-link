"""
  @project setup.py
  @Package 
  @author WeiJingqi
  @date 2023/11/27 - 17:02
  代码装饰器
 """
from tests.Rewrite import NodeManager
from tests.Display import *


def register(f):    # 每次调用注册器都会生成一个manager，解决这个问题
    manager = NodeManager()
    print(f"init manager{manager}")

    def wrapper(x):
        # manager.create_node()
        ret = f(x)
        name = ret.name
        dict = ret.dict
        new_node = manager.create_node(name, dict)
        return new_node

    return wrapper


@register
class DatasetDict:
    dict = []
    name = None

    def __init__(self, name) -> None:
        self.dict = {'iris': Iris().data_dict,
                     'wine': Wine().data_dict}
        self.name = name


@register
class SplitDict:
    dict = []
    name = None

    def __init__(self, name) -> None:
        self.dict = {'ratio:0.8': TestSplitter(0.8),
                     'ratio:0.5': TestSplitter(0.5)}
        self.name = name


if __name__ == '__main__':
    dataset = DatasetDict("dataset")
    spliter = SplitDict("data_split")
    print(spliter.manager)
    print(dataset.manager)
    print(0)
# def register(class_name):  # timeit(100000)
#     manager = NodeManager()
#     if class_name == "dataset":
#         def inner(f):  # f就是调用的函数
#             def wrapper(*args, **kwargs):  # *args, **kwargs是调用方法调用方法中传入的参数
#
#                 ret = f(manager, *args, **kwargs)  # 执行f方法得到结果ret，注册节点时候需要传入manager
#
#                 return ret  # 最终返回的结果，会一层层返回
#
#             return wrapper
#
#         return inner
