"""
  @project setup.py
  @Package 
  @author WeiJingqi
  @date 2023/11/27 - 9:39
 """


def get_multiple_func(n):
    def multiple(x):
        return n * x
    return multiple


if __name__ == '__main__':
    double = get_multiple_func(2)
    triple = get_multiple_func(3)

    print(double(3))
    print(triple(3))
