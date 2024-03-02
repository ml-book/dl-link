"""
  @project setup.py
  @Package 
  @author WeiJingqi
  @date 2023/11/27 - 9:45
 """


class A:

    def __init__(self) -> None:
        super().__init__()


def dec(f):
    return 1


@dec
def double(x):
    return x * 2


# 完全等价于
double = dec(double)
print(double)
# print(double(2))
