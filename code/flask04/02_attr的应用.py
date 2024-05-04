# class Foo:
#     pass
#
# obj = Foo()
# obj.x1 = 123
# print(obj.x1)
#


class Local(object):
    def __init__(self):
        # self.storage = {}
        object.__setattr__(self,"storage",{})

    def __setattr__(self, key, value):
        print("__setattr__已经调用")
        self.storage[key] = value

    def __getattr__(self, item):
        print("__getattr__已经调用")
        return self.storage.get(item)

local = Local()
local.x1 = 123
print(local.x1)