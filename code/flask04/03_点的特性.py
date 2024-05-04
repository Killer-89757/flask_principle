# 通过下面的代码更清晰直观的了解.点的特性
class ClassA(object):

    def __init__(self, classname):
        self.classname = classname

    def __getattr__(self, attr):
        return('invoke __getattr__', attr)

insA = ClassA('ClassA')
print(insA.__dict__) # 实例insA已经有classname属性了
# {'classname': 'ClassA'}

print(insA.classname) # 不会调用__getattr__
# ClassA

print(insA.grade) # grade属性没有找到，调用__getattr__
# ('invoke __getattr__', 'grade')