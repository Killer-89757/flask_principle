class Foo:
    def __init__(self):
        self.name = 'alex'
        self.__age = 123


obj = Foo()

print(obj.name)
# 不符合开发规范，但是确实可以用
print(obj._Foo__age)
