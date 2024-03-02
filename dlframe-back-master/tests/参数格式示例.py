import ast

params = [{'dataset': {'IRIS', 'WINE'},
           'data_split': {'ratio': {0.8, 0.5}},
           'model': {'SVM': {'kernel': ['default']}},
           'judger': {'judge_clf', 'judge_rlf'}
           }]
real_params = [{'dataset': {'Wine': {}, 'Iris': {}}},
               {'data_split': {'TestSplitter': {'ratio': [0.8, 0.5]}}},
               {'model': {'SVM': {'kernel': ['default']}}},
               {'judger': {'TestJudger': {'model_class': [0, 1]}}}]

version3 = [{'dataset': {'Iris': {}, 'Wine': {}}},
            {'data_split': {'TestSplitter': {'ratio': [0.8, 0.5]}}},
            {'model': {'LinearRegression': {}, 'SVM': {'kernel': ['default']}}},
            {'judger': {'Judger_Clf': {}, 'Judger_Rlf': {}}}]



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
    }]'''

version4 = [{'title': 'dataset',
             'options': [{'name': 'Wine', 'args': {}},
                         {'name': 'Wine', 'args': {}}]},
            {'title': 'data_split',
             'options': [{'name': 'TestSplitter', 'args': {'ratio': [0.8, 0.5]}}]},
            {'title': 'model', 'options': [{'name': 'LinearRegression', 'args': {}},
                                           {'name': 'LinearRegression', 'args': {}}]},
            {'title': 'judger',
             'options': [{'name': 'Judger_Clf', 'args': {}},
                         {'name': 'Judger_Clf', 'args': {}}]}]

'''
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
        params = []
        for k in class_dict:    # k: model dataset
            class_set = {}
            model = {}
            for c in class_dict[k]:     # c: svm iris wine
                each_set = {}
                for each_k in c().get_params():
                    each_list = []
                    for each in c().get_params()[each_k]:
                        each_list.append(each)
                    each_set[each_k] = each_list
                model[c().__class__.__name__] = each_set    # each_set 可能是空字典
            class_set[k] = model
            params.append(class_set)
        return params
'''

if __name__ == '__main__':
    str = str({
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
    print(str)
    str = "{'dataset': 'iris', 'data_split': 'ratio:0.8', 'model': {'name': 'svm', 'params': {'kernel': 'default'}}, 'judger': 'judge_clf'}"
    dict = ast.literal_eval(str)
    print(dict)