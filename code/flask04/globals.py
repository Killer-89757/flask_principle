from lk import LocalStack

# 在这个文件创建，在其他文件引用就是单例模式，因为只生成了1次
context = LocalStack()
app_context = LocalStack()