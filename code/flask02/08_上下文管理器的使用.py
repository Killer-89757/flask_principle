class Foo(object):

    def __enter__(self):
        print("执行enter函数")
        return 123

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("执行exit函数")

obj = Foo()

with obj as f:
    print(f)