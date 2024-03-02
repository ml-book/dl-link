# from typing import List
import math
import threading
import queue
from typing import Any
from enum import Enum

from tests.Display import Iris, Wine, TestSplitter, TestJudger, Judger_Clf, Judger_Rlf
from tests.Model.KNN import KNN
from tests.Model.LinearRegression import LinearRegression
from tests.Model.svm import SVM


class NodeType(Enum):
    BASE_ELEMENT_NODE = 1,
    GET_ATTR_NODE = 2,
    FUNCTION_CALL_NODE = 3


# 注意，改个名字 CalculationNode
class CalculationNode:
    next_nodes: list
    prev_nodes: list
    # name-->node_name
    node_name: str
    exec_current_in_degree: int
    elements: dict

    manager: Any

    exec_result: Any

    node_type: NodeType

    pre_link_nodes: list

    def __init__(self, manager, node_name: str, elements=None, node_type=None, pre_link_nodes=None,
                 auto_edge_connection=True) -> None:
        if pre_link_nodes is None:
            pre_link_nodes = []
        self.pre_link_nodes = pre_link_nodes
        self.prev_nodes = []
        self.next_nodes = []
        self.node_name = node_name
        if elements is None:
            elements = {}
        self.elements = elements
        self.exec_current_in_degree = None
        if node_type is None:
            node_type = NodeType.BASE_ELEMENT_NODE
        self.node_type = node_type

        self.manager = manager

        if auto_edge_connection:
            for node in self.pre_link_nodes:
                node._create_edge(self)

        manager._register_node(self)

    def _create_edge(self, next_node):
        # print(f"cur_nodeName:{self.node_name}--->next_nodeName:{next_node.node_name}")
        self.next_nodes.append(next_node)
        next_node.prev_nodes.append(self)

    def _execute(self, config: dict): # 这里的问题，大部分时候以下三种情况中第一和第三种都有可能出现类似阻塞的bug，第三种情况出现bug概率更大
        if self.node_type == NodeType.BASE_ELEMENT_NODE and len(self.elements) != 0:
            element_config = config.get(self.node_name)
            has_params = True
            if type(element_config) != dict:
                has_params = False
                element_config = {
                    'name': element_config,
                    'params': {}
                }
            element_name = element_config['name']
            # if element_name == 'svm':
            #     print(0)
            element_params = element_config['params']  # element_params = {'p1': 'aaa', 'p2': 'bbb'}
            #########
            # if has_params:
            #     value_list = [value for value in element_params.values()] #重写value()
            #########
            print(self.elements)
            print(element_name)
            self.exec_result = self.elements.get(element_name)
            if has_params and hasattr(self.exec_result, 'set_params'):
                self.exec_result.set_params(element_params)
        elif self.node_type == NodeType.GET_ATTR_NODE:
            father_element = self.prev_nodes[0].exec_result
            self.exec_result = getattr(father_element, self.node_name)
        elif self.node_type == NodeType.FUNCTION_CALL_NODE:
            father_element = self.prev_nodes[0].exec_result
            args = [i.exec_result if type(i) == CalculationNode else i for i in self.node_name['args']]
            kwargs = {k: v.exec_result if type(v) == CalculationNode else v for k, v in
                      self.node_name['kwargs'].values()}
            self.exec_result = father_element(*args, **kwargs)

        else:
            raise NotImplementedError('unknown node type')

    def __getattr__(self, __name: str):
        if __name != '__getitem__':
            self.manager.link_nodes.append(__name)  # 要在manager里维护，因为每个计算节点对象不一样

        if __name == '__iter__':
            return None
        next_node = CalculationNode(self.manager, __name, node_type=NodeType.GET_ATTR_NODE)
        self._create_edge(next_node)
        return next_node

    def __call__(self, *args: Any, **kwds: Any):

        next_node = CalculationNode(self.manager, {
            'args': args,
            'kwargs': kwds
        }, node_type=NodeType.FUNCTION_CALL_NODE, pre_link_nodes=[self])
        # self._create_edge(next_node)

        for arg in args:
            if type(arg) == CalculationNode:
                arg._create_edge(next_node)
        for key, arg in kwds:
            if type(arg) == CalculationNode:
                arg._create_edge(next_node)
        return next_node

    def __getitem__(self, index):
        return self.__getattr__('__getitem__')(index)

    def __lt__(self, rhs):  # 实际上应该连接的是具体执行功能的边吗，即functionNode？？？如果是那就应该拿到节点名字，找到其功能执行Node并连接
        """
        重载运算符'<'，对前后两个对象加一条有向边
        @param rhs: 双目运算符的对象2
        """
        rhs.next_nodes.append(self)
        self.prev_nodes.append(rhs)
        if rhs.exec_current_in_degree is None:
            self.exec_current_in_degree = 1
        else:
            self.exec_current_in_degree += 1

    def __gt__(self, other):
        """
        重载运算符'>'，对前后两个对象加一条有向边
        @param other: 双目运算符的对象2
        """
        self.next_nodes.append(other)
        other.prev_nodes.append(self)
        if other.exec_current_in_degree is None:
            other.exec_current_in_degree = 1
        else:
            other.exec_current_in_degree += 1


def execute_all_nodes(manager, config, max_size=0):
    all_nodes = manager.all_nodes

    node_queue = queue.Queue(maxsize=max_size)

    last_node = None

    for node in all_nodes:
        ''' 能否在train和test之间手动连一条边
            father_element = self.prev_nodes[0].exec_result在实际访问函数
        '''
        # if node.node_type == NodeType.FUNCTION_CALL_NODE and node.prev_nodes[0].node_name in manager.link_nodes:
        #     if last_node is not None:
        #         last_node > node
        #     last_node = node

        node.exec_current_in_degree = len(node.prev_nodes)

        if node.exec_current_in_degree == 0:
            node_queue.put(node)

    while not node_queue.empty():
        current_node = node_queue.get()
        # print(current_node.node_name)
        # 实际的遍历操作
        current_node._execute(config)

        for next_node in current_node.next_nodes:
            if next_node.exec_current_in_degree != None:
                next_node.exec_current_in_degree -= 1
                if next_node.exec_current_in_degree == 0:
                    node_queue.put(next_node)

class NodeManager:
    all_nodes: list
    registed_nodes = {}
    last_func_node: CalculationNode
    relast_func_node: CalculationNode
    link_nodes = []  # 存放需要链接的节点的名称
    num = 1

    def __init__(self, if_parallel=False) -> None:  # 是否并行化, 是false才加边
        self.all_nodes = []
        self.last_func_node = None
        self.relast_func_node = None
        self.parallel = if_parallel

    def _register_node(self, node):
        if not self.parallel:  # 无需并行化处理则连接function_node

            if node.node_type == NodeType.FUNCTION_CALL_NODE:
                if self.last_func_node is not None:
                    self.last_func_node > node
                self.last_func_node = node

        self.all_nodes.append(node)  # 方法原本的内容

    def create_node(self, name: str, ele_dict: dict):
        return CalculationNode(self, name, ele_dict)

    def get_all_params(self):  # 创建一个高维字典，然后创建节点获取其get_params方法
        """
        形式{ 'model': {'svm', 'knn'},
             'dataset': {'iris', 'wine'},
            }
        @return:
        """
        class_dict = {'dataset': {Iris, Wine},
                      'data_split': {TestSplitter},
                      'model': {SVM, LinearRegression},
                      'judger': {Judger_Clf, Judger_Rlf}}

        '''
        receiveData: [
    {
        title: "算法",
        options: [
            {
                name: "SVM", args: { kernal: ["default","linear","ploy"],depth:[1,2,3] }
            },
            {
                name: "d_tree", args: { depth: [5,10,20,30] }
            },
            {
                name: "KNN", args: { cluster: [3,5,7,9] }
            }]
    },
    {
        title: "数据集",
        options: [
            { name: "红酒", args: {num:[10,20,30]} },
            { name: "鸢尾花", args: {num:[10,20,30]} },
            { name: "波士顿", args: {num:[10,20,30]} }
        ]
        '''
        params = []
        for k in class_dict:    # k: model dataset
            class_set = {}
            class_set['title'] = k
            model = {}
            models = []
            for c in class_dict[k]:     # c: svm iris wine
                each_set = {}
                for each_k in c().get_params():
                    each_list = []
                    for each in c().get_params()[each_k]:
                        each_list.append(each)
                    each_set[each_k] = each_list
                model['name'] = c().__class__.__name__
                model['args'] = each_set    # each_set 可能是空字典
                models.append(model)
            class_set['options'] = models

            params.append(class_set)
        return params

#
# # from Display-old import TestDataset, TestJudger, TestModel, TestSplitter
# from Display_old import TestDataset, TestJudger, TestModel, TestSplitter
#
# if __name__ == '__main__':
#     # 创建图
#     # 创建节点
#     # node1 = Node("node1")
#     # node2 = Node("node2")
#
#     # # 创建边
#     # node1._create_edge(node2)
#
#     manager = NodeManager()
#
#     dataset = CalculationNode(manager, '数据集', {'10_nums': TestDataset(10), '20_nums': TestDataset(20)})
#     splitter = CalculationNode(manager, '数据分割', {'ratio:0.8': TestSplitter(0.8), 'ratio:0.5': TestSplitter(0.5)})
#     model = CalculationNode(manager, '模型', {'model1': TestModel(1e-3)})
#     judger = CalculationNode(manager, '评价指标', {'judger1': TestJudger()})
#
#     train_data_test_data = splitter.split(dataset)
#     train_data, test_data = train_data_test_data[0], train_data_test_data[1]
#     model.train(train_data)
#     y_hat = model.test(test_data)
#     judger.judge(y_hat, test_data)
#
#     # print('--------------------------')
#     # print(manager.all_nodes)
#
#     # 遍历图
#     execute_all_nodes(manager.all_nodes, {
#         '数据集': '10_nums',
#         '数据分割': 'ratio:0.8',
#         '模型': {
#             'name': 'model1',
#             'params': {
#                 'p1': 'aaa',
#                 'p2': 'bbb'
#             }
#         },
#         # '模型': 'model1',
#         '评价指标': 'judger1'
#     })
#
#     print('---------------------')
#     # for node in manager.all_nodes:
#     #     print(f'name:{node.name},node-elements{node.elements}')
