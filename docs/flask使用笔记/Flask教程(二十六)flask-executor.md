# Flask教程(二十六)flask-executor

## 环境

- windows 10 64bit
- anaconda3 with python 3.7
- flask 1.1.2
- flask-executor 0.10.0

## 前言

本篇介绍 `flask` 的另一个扩展，即 `flask-executor`，它将 `python` 中的 `concurrent.futures` 功能加到了 `flask` 中，使得我们在 `flask` 中使用任务队列变得非常的方便。

## 安装

直接使用 `pip` 安装

```
pip install flask-executor
```

## 基本使用

下面这个例子来自官方，模拟的是用户在网站注册账号时，网站发送电子邮件到用户邮箱的动作，看下面的代码

```python
from flask import Flask
from flask_executor import Executor
app = Flask(__name__)
# 实例化
executor = Executor(app)
def send_email(recipient, subject, body):
    # 模拟邮件发送动作
    print('send mail.')
    return True
@app.route('/signup')
def signup():
    # 将任务send_email放进任务池中
    executor.submit(send_email, "test@gmail.com", "subject", "body")
    return "signup done."
if __name__ == '__main__':
    # 启动服务
    app.run('0.0.0.0', debug=True, port=5000)
```

代码部分没什么可解释的，`flask-executor` 与其它扩展的使用方法一样。通过方法 `submit` 将任务放进任务池中，依次执行。

## 几个配置

默认情况下，`flask-executor` 使用的是线程池，可以通过设置 `EXECUTOR_TYPE` 来指定使用进程池

```python
# 值为 process 或者 thread
app.config['EXECUTOR_TYPE'] = 'process'
```

除了 `executor` 的类型，还有个值非常重要，就是池子的大小。可以通过设置 `EXECUTOR_MAX_WORKERS` 来指定

```python
app.config['EXECUTOR_MAX_WORKERS'] = 10
```

## 装饰器

`flask-executor` 提供了装饰方法的方法，看下面示例

```python
@executor.job
def fib(n):
    if n <= 2:
        return 1
    else:
        return fib(n-1) + fib(n-2)
@app.route('/decorate_fib')
def decorate_fib():
    fib.submit(5)
    return 'OK'
```

## 回调

`concurrent.futures.Future` 对象可以通过方法 `add_done_callback` 来绑定回调，来看下面代码片段

```python
def callback(future):
    print('callback')
    
@app.route('/signup')
def signup():
    executor.add_default_done_callback(callback)
    executor.submit(send_email, "test@gmail.com", "subject", "body")
    return "signup done."
```

当 `send_email` 完成后，回调函数 `callback` 就会被执行

## 参考资料

- https://github.com/dchevell/flask-executor
- https://flask-executor.readthedocs.io/en/latest/