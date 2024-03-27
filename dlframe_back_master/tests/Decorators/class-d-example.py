"""
  @project setup.py
  @Package 
  @author WeiJingqi
  @date 2023/12/12 - 15:16
 """


class Count:
    def __init__(self, a):  # 类装饰器参数
        self.a = a
        self.num_calls = 0

    def __call__(self, func):  # 被装饰函数
        print(self.a)

        def wrapper(*args, **kwargs):
            print(self.a)
            self.num_calls += 1
            print('num of calls is: {}'.format(self.num_calls))
            return func(*args, **kwargs)

        return wrapper


@Count("aaaa")
def example():
    print("hello world")


# example = Count("aaaa")(example)

example()
