class Foo(object):

    def do_somthing(self):
        print("do something")

    def close(self):
        print("close")


# 使用context去管理Foo类的执行和关闭
class Context:
    def __enter__(self):
        self.data = Foo()
        return self.data

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.data.close()


with Context() as ctx:
    ctx.do_somthing()