"""
  @project dlframe-back-master
  @Package 
  @author WeiJingqi
  @date 2023/11/8 - 17:27
 """
import numpy as np


class LinearRegression:     # 6.1
    def __init__(self):
        # 系数向量（θ1,θ2,.....θn）
        self.coef_ = None
        # 截距 (θ0)
        self.interception_ = None
        # θ向量
        self._theta = None
        self.args = {}

    def set_params(self, args):
        self.args = args
        print('--------------------set_lr_args----------------------')
        # 储存args，参数是事先约定好的，然后设置参数或者方法调用时从args中选择

    def get_params(self):   # 在manager中实现获取到每个模型的get_params
        return self.args

    def fit(self, X_train, y_train):
        assert X_train.shape[0] == y_train.shape[0], \
            "the size of X_train must be equal to the size of y_train"
        X_b = np.hstack([np.ones((len(X_train), 1)), X_train])
        self._theta = np.linalg.inv(X_b.T.dot(X_b)).dot(X_b.T).dot(y_train)
        self.interception_ = self._theta[0]
        self.coef_ = self._theta[1:]
        return self

    def predict(self, X_predict):
        assert self.coef_ is not None and self.interception_ is not None, \
            "must fit before predict"
        assert X_predict.shape[1] == len(self.coef_), \
            "the feature number of X_predict must be equal to X_train"
        X_b = np.hstack([np.ones((len(X_predict), 1)), X_predict])
        return X_b.dot(self._theta)
