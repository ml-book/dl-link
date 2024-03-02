"""
  @project setup.py
  @Package 
  @author WeiJingqi
  @date 2023/12/12 - 15:52
 """
# 装饰器1
def deco1(func):
    def wrapper(*args, **kwargs):
        print("deco1开始")
        result = func(*args, **kwargs)
        print("deco1结束")
        return result
    return wrapper

# 装饰器2
def deco2(func):
    def wrapper(*args, **kwargs):
        print("deco2开始")
        result = func(*args, **kwargs)
        print("deco2结束")
        return result
    return wrapper

@deco1
@deco2
def example():
    print("被装饰函数！")

# 调用
example()

# 调用结果
# >>deco1开始
# >>deco2开始
# >>被装饰函数！
# >>deco2结束
# >>deco1结束
