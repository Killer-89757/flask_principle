# Flask教程(二十三)简单异步任务

### 软硬件环境

- windows 10 64bit
- anaconda3 with [python](https://xugaoxiang.com/tag/python/) 3.7
- [flask](https://xugaoxiang.com/tag/flask/) 1.1.2

### 前言

从`Python` 3.2开始，标准库为我们提供了`concurrent.futures`模块，它提供了`ThreadPoolExecutor`(线程池)和`ProcessPoolExecutor`(进程池)两个类。使用`submit`方法来提交线程(或进程)需要执行的任务到线程(进程)池中，并返回该任务的句柄，`submit`不是阻塞的，而是立即返回。通过任务句柄的`done()`方法来判断该任务是否结束，通过`result()`方法可以获取任务的返回值。

结合`concurrent.futures`模块，可以在`flask`应用中实现简单异步任务。

### 代码实现

直接来看代码吧

```python
from flask import Flask
import time
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(2)
app = Flask(__name__)


@app.route('/tasks')
def run_background_tasks():
    # 提交2个任务，一个带参、一个不带参
    executor.submit(background_task1)
    executor.submit(background_task2, 'hello', 'future')
    return 'tasks started in background!'


def background_task1():
    print("background_task1 started!")
    time.sleep(10)
    print("background_task1 done!")


def background_task2(arg1, arg2):
    print(f"background_task2 started with args: {arg1} {arg2}!")
    time.sleep(5)
    print("background_task2 done!")


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
```

启动`flask`服务后，访问`http://127.0.0.1:5000/tasks`，观察终端的打印输出

![flask_future](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F86cbead7ab67bc36-854460.png)