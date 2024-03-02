"""
  @project setup.py
  @Package 
  @author WeiJingqi
  @date 2024/2/24 - 16:38
 """
from tests.Rewrite_main import NodeManager


def register(para1, para2="default"):  # para1:"dataset" ,para2: wine/iris
    def inner(class_name):  # 类名
        def wrapper(*args):  # 由类初始化传入manager
            print(args)
            manager = args[0]
            class_params = args[1:]
            print(class_params)
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
                registed_node.elements[para_name] = ret.data_dict  # 向字典内添加

            else:  # 未注册，注册当前节点
                new_node = manager.create_node(para1, {para_name: ret})  # 产生的Node
                manager.registed_nodes[para1] = new_node  # 注册节点

            return ret

        return wrapper

    return inner  # 返回的还是类对象本身，而产生的Node用字典存起来，使用时候再返回


@register('Aaa')
class A():
    ratio: float

    def __init__(self, ratio) -> None:
        self.ratio = ratio
        super().__init__()

    def print_ratio(self):
        print(self.ratio)


@register('Bbb')
class B():

    def __init__(self) -> None:
        super().__init__()

    def print_ratio(self):
        print('我没有参数')


if __name__ == '__main__':
    manager = NodeManager(if_parallel=False)
    A(manager, 0.5)
    print(1)
    B(manager)
    print(0)
