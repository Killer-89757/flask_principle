# Flask教程(二)第一个Flask应用程序

### 软硬件环境

- Windows 10 64bit
- Anaconda3 with [python](https://xugaoxiang.com/tag/python/) 3.7
- PyCharm 2019.3
- Flask 1.1.1

### 前言

在配置好[`Flask`开发环境](https://xugaoxiang.com/2020/03/12/flask-1-intro/)后，我们就要开始编写第一个`Flask`应用程序了。

打开集成开发环境`PyCharm`，由于`IDE`已经集成了`Flask`的组件，因此我们在创建工程的时候，可以直接创建`Flask`项目，如下图所示

![flask](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F6c439404863a4a67-27f7d7.png)

关于模板，我们后面会讲到，这里就直接默认选择`Jinja2`就好。进入到工程后，我们新建一个`python`文件`run.py`，然后在文件输入以下代码

```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, flask!"

if __name__ == '__main__':
    app.run(host="127.0.0.1",port=5000,debug=True)
```

接着我们来运行这个工程，点击菜单栏上的`Run`-->`Run "run"`，或者鼠标右击文件`run.py`选择`run`，程序就启动了

![flask](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F16f2eb519c16124a-80b058.png)

这时候，我们来到浏览器，在地址栏中输入`127.0.0.1:5000`

![flask](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F9a2f0c52cf97f70c-7f3cd8.png)

可以看到页面的内容是`Hello flask!`。

最后来解释下上面的代码，语句

> ```python
> app = Flask(__name__)
> ```

是创建`Flask`对象，把当前模块的名称作为参数传递进去

> ```python
> @app.route('/')
> ```

定义了一个路由，它是函数`index`的装饰器，整个的意思就是`/`路由是由`index`这个函数来处理的。关于路由，后面我们会有完整的一节来介绍。

最后就是`Flask`程序的启动了

> ```python
> app.run(host="127.0.0.1",port=5000,debug=True)
> ```

使用`Flask`对象的`run`方法，这里我们指定`run`的参数`debug`为`True`，就是打开调试信息的意思。可以看到当我们执行`Flask`应用程序时，`Flask`会开启一个其自带的`web`服务器，这个服务器在代码调试时非常有用，也非常方便，但是不建议在生成环境中使用。