"""
  @project setup.py
  @Package 
  @author WeiJingqi
  @date 2023/11/27 - 9:49
 """

import time


def timeit(f):

    def wrapper(x):
        start = time.time()
        ret = f(x)
        print(time.time() - start)
        return ret

    return wrapper


@timeit
def my_func(X):
    time.sleep(X)


my_func(1)
my_func(2)