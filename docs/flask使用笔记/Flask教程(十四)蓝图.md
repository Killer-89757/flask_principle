# Flask教程(十四)蓝图

### 软硬件环境

- windows 10 64bit
- [anaconda](https://xugaoxiang.com/tag/anaconda/)3 with [python](https://xugaoxiang.com/tag/python/) 3.7
- pycharm 2020.1.2
- [flask](https://xugaoxiang.com/tag/flask/) 1.1.2

### 什么是蓝图

蓝图(`blueprint`)提供了**模块化管理程序路由**的功能，使程序结构清晰、简单易懂。`blueprint`对象和`flask`应用对象的工作方式很像，但他俩不是一个东西。蓝图很好地简化了大型应用工作的方式，并提供给`flask`扩展在应用上注册操作的核心方法。

### 应用工厂函数

前面讲到常见`flask`项目结构时提到一点，在单个文件中开发应用很方便，但是有个很大的缺点，应用在全局作用域中创建，无法动态修改配置。运行脚本时，应用实例已经创建，再修改配置已经为时已晚。面对这个问题，解决方案就是延迟创建应用实例，这时工厂函数就出场了，来看下面的示例

```python
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from app.config import Config

bootstrap = Bootstrap()
db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    bootstrap.init_app(app)
    db.init_app(app)

    return app
```

首先导入了大多数正在使用的`flask`扩展，但是由于尚未初始化所需的应用实例，所以创建扩展类时没有向构造函数传入参数，因此扩展并未真正初始化。`create_app`函数是应用的工厂函数，接受一个参数，是应用使用的配置名。配置类在`config.py`文件中定义。应用创建并配置好后，就能初始化扩展了。在之前创建的扩展对象上调用`init_app()`便可以完成初始化

### 为什么使用蓝图

来看看蓝图的优点，来自官方文档

- 把一个应用分解为一个蓝图的集合。这对大型应用是理想的。一个项目可以实例化一个应用对象，初始化几个扩展，并注册一集合的蓝图
- 以`URL`前缀和`/`或子域名，在应用上注册一个蓝图。`URL`前缀`/`子域名中的参数即成为这个蓝图下的所有视图函数的共同的视图参数（默认情况下）
- 在一个应用中用不同的`URL`规则多次注册一个蓝图
- 通过蓝图提供模板过滤器、静态文件、模板和其它功能。一个蓝图不一定要实现应用或者视图函数。
- 初始化一个`Flask`扩展时，在这些情况中注册一个蓝图

蓝图作为`flask`层提供分割的替代，共享应用配置，并且在必要情况下可以更改所注册的应用对象。它的缺点是你不能在应用创建后撤销注册一个蓝图而不销毁整个应用对象。

### 蓝图示例

结合上面的应用工厂和蓝图，我们来看看示例，工程结构如下

```python
blueprint/
  app/
      static/
        ...

      views/
        index.py

      templates/
        ...

      __init__.py

      config.py

  manage.py
  README.md
  requirements.txt
```

其中`manage.py`代码如下

```python
from app import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(use_reloader=True, port=5000)
```

`__init__.py`代码如下

```python
from flask import Flask
from .views.index import index_blueprint
from . import config


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    app.register_blueprint(index_blueprint)

    return app
```

`index.py`源码如下

```python
from flask import Blueprint

index_blueprint = Blueprint('index', __name__)

@index_blueprint.route('/')
def index():
    return "Hello blueprint."
```

`config.py`存放的是相关的配置信息

```python
DEBUG = False
```

当上述项目启动后，我们就可以访问`http://127.0.0.1:5000`，浏览器输出`Hello blueprint.`

### 如何组织蓝图

`flask`中同样没有规定你如何来组织蓝图。常见的，有按照功能(`functional`)和按照分区(`divisional`)这2种方式来组织。

在功能架构中，按照每部分代码的功能来组织你的应用。所有模板、静态文件和视图都单独放在一个文件夹中，如下

```python
project/
    app/
        __init__.py
        static/
        templates/
            home/
            admin/
        views/
            __init__.py
            home.py
            admin.py
        models.py
        config.py

    README.md
    requirements.txt
    manage.py
```

除了`project/app/views/__init__.py`，在`project/app/views/`文件夹中的每一个`.py`文件都是一个蓝图。在`project/app/__init__.py`中，加载这些蓝图并在`flask`对象中注册。

而在分区式架构中，按照每一部分所属的蓝图来组织你的应用。所有的模板、视图和静态文件放在一个文件夹中。项目结构如下

```python
project/
    app/
        __init__.py
        admin/
            __init__.py
            views.py
            static/
            templates/
        home/
            __init__.py
            views.py
            static/
            templates/
        models.py
        config.py

    README.md
    requirements.txt
    manage.py
```

在上面的分区式结构，每一个`project/app/`之下的文件夹都是一个独立的蓝图。所有的蓝图通过顶级的`__init__.py`注册到`flask`对象中。

至于说，上面两种结构孰优孰劣，这个没有定论。一般的建议是这样的：如果应用是由独立的且仅仅共享模型和配置的各组件组成，建议选择分区式；如果应用的组件之间联系较为紧密，则建议使用功能式架构。