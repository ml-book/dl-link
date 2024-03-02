"""
  @project dlframe-back-master
  @Package 
  @author WeiJingqi
  @date 2023/10/23 - 11:02
 """
from tests.Decorator import DatasetDict, SplitDict, ModelDict, JudgeDict
from tests.Display import TestSplitter
from tests.Rewrite_main import NodeManager, execute_all_nodes


if __name__ == '__main__':

    # 注册所需的参数节点 如0.8 然后在 spliter = manager.registed_nodes["data_split"] 时传入0.8的节点

    manager = NodeManager(if_parallel=False)
    manager.get_all_params()
    DatasetDict(manager)
    # SplitDict(manager)
    ModelDict(manager)
    JudgeDict(manager)
    dataset = manager.registed_nodes["dataset"]
    # spliter = manager.registed_nodes["data_split"]

    # manager.register("ratio", {"0.8": 0.8, "0.5": 0.5})
    ratio_node = manager.create_node("ratio", {"0.8": 0.8, "0.5": 0.5})
    manager.registed_nodes['ratio'] = ratio_node
    # Spliter = manager.registed_nodes["data_split"]
    Spliter = manager.create_node("data_split", {TestSplitter()})
    ratio = manager.registed_nodes["ratio"]
    spliter = Spliter.set_params(ratio)
    # 改为Spliter(ratio)  # spliter = Spliter(manager.CUSTOM_PARAMS) 识别如果是构造函数，传入个性化参数
    # CUSTOM_PARAMS常量设置为，如果要用个性化参数就使用spliter = Spliter(manager.CUSTOM_PARAMS)方式
    # 在Node中再加一个变量，表明是否使用个性化参数，在魔法方法function_call时候判断是否使用

    model = manager.registed_nodes["model"]
    judger = manager.registed_nodes["judger"]


    split_result = spliter.split(dataset)
    X_train, X_test, y_train, y_test = (split_result[i] for i in range(4))
    model.fit(X_train, y_train)
    # temp = model.train(X_train, y_train)
    # temp > predict 实现temp优先于predict计算
    y_predict = model.predict(X_test)
    judger.judge(y_test, y_predict)

    execute_all_nodes(manager, {
        'dataset': 'iris',
        'data_split': 'ratio:0.8',
        'model': {
                'name': 'svm',
                'params': {
                    'kernel': 'default'
                }
            },
        'judger': 'judge_clf'
    })
    print(0)

