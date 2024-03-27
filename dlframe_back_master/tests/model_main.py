"""
  @project dlframe-back-master
  @Package 
  @author WeiJingqi
  @date 2023/10/23 - 11:02
 """
from tests.Decorator import DatasetDict, SplitDict, ModelDict, JudgeDict
from tests.Display import TestSplitter, TestModel, TestJudger, Iris, Wine
from tests.Model.DecisionTree import DecisionTree
from tests.Model.KNN import KNN
from tests.Model.K_Means import K_Means
from tests.Model.LinearLogisticRegression import LinearLogisticRegression
from tests.Model.Random_Forest import Random_Forest
# from tests.Test import Random_Forest
from tests.Model.svm import SVM
from tests.Rewrite import NodeManager, execute_all_nodes
from tests.Model.LinearRegression import *

# with WebManager(parallel=False) as manager:
# WebManager继承NodeManager，还需要改一下NodeManager，初始化添加parallel参数，让其实现并行化？？？
# 看一下原本的CalculationNodeManager是怎么写的
if __name__ == '__main__':
    manager = NodeManager()
    is_re = 0   # 是否是回归算法
    DatasetDict(manager)
    SplitDict(manager)
    ModelDict(manager)
    JudgeDict(manager)
    dataset = manager.registed_nodes["dataset"]
    spliter = manager.registed_nodes["data_split"]
    model = manager.registed_nodes["model"]
    judger = manager.registed_nodes["judger"]
    # data_dict = {'iris': Iris().data_dict,
    #              'wine': Wine().data_dict}
    # split_dict = {'ratio:0.8': TestSplitter(0.8),
    #               'ratio:0.5': TestSplitter(0.5)}
    # model_dict = {'LinearRegression': LinearRegression(),
    #               'DecisionTree': DecisionTree(),
    #               'LinearLogisticRegression': LinearLogisticRegression(),
    #               'KNN': KNN(),
    #               'svm': SVM(),
    #               'RandomForest': Random_Forest(),
    #               'k-means': K_Means()}
    # judge_dict = {'judge_clf': TestJudger(is_re)}
    #
    # dataset = manager.create_node('dataset', data_dict)
    # spliter = manager.create_node('data_split', split_dict)
    # model = manager.create_node('model', model_dict)
    # judger = manager.create_node('judger', judge_dict)

    split_result = spliter.split(dataset)
    X_train, X_test, y_train, y_test = (split_result[i] for i in range(4))
    model.fit(X_train, y_train)
    # temp = model.train(X_train, y_train)
    # temp > predict 实现temp优先于predict计算
    y_predict = model.predict(X_test)
    judger.judge(y_test, y_predict)

    execute_all_nodes(manager.all_nodes, {
        'dataset': 'iris',
        'data_split': 'ratio:0.8',
        # 'model': {
        #     'name': 'svm',
        #     'params': {
        #         'p1': 0.01,
        #         'p2': 'svm',
        #         'p3': 0
        #     }
        # },
        'model': 'svm',
        'judger': 'judge_clf'
    })
    print(0)
'''
实现并行化模块和装饰器注册

参照github

    并行化加边
    parallel是true要手动加边的接口
        重载运算法大于小于，用于边的方向确定 是对选定的节点加边还是具体的执行节点，对选定的节点加边可能没有用？
        加边不能忘记增加入度
'''
