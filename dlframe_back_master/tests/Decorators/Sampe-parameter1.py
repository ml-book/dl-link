"""
  @project setup.py
  @Package 
  @author WeiJingqi
  @date 2023/11/27 - 11:08
 """

import time


def timeit(iteration):  # timeit(100000)
    def inner(f):   # f就是double函数
        def wrapper(*args, **kwargs):   # *args, **kwargs是调用方法double中传入的参数
            start = time.time()
            for _ in range(iteration):
                ret = f(*args, **kwargs)    # 执行f方法double得到结果ret
            print(time.time() - start)
            return ret  # 最终返回的结果，会一层层返回

        return wrapper

    return inner


@timeit(100000)
def double(x):
    return x * 2


print(double(2))

# 等价于
# inner = timeit(100000)
# double = inner(double)
#
# double(2)
