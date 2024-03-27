"""
  @project setup.py
  @Package 
  @author WeiJingqi
  @date 2023/11/27 - 9:49
 """

import time


def timeit(f):
    def wrapper(*args, **kwargs):
        start = time.time()
        ret = f(*args, **kwargs)
        print(time.time() - start)
        return ret

    return wrapper


@timeit
def my_func(X):
    time.sleep(X)


@timeit
def add(x, y):
    return x + y



my_func(1)
print(add(2, 3))

# 等价于
double = timeit(10)(double)  # 先执行timeit(10)
