class Foo(object):

    def __setattr__(self, key, value):
        print("__setattr__执行")
        print(key, value)

    def __getattr__(self, item):
        print("__getattr__执行")
        print(item)


obj = Foo()
obj.x = 123
obj.x

"""
__setattr__执行
x 123
__getattr__执行
x
"""