# Flask教程(十六)RESTful-API

### 软硬件环境

- windows 10 64bit
- anaconda3 with [python](https://xugaoxiang.com/tag/python/) 3.7
- pycharm 2020.1.2
- [flask](https://xugaoxiang.com/tag/flask/) 1.1.2
- [flask](https://xugaoxiang.com/tag/flask/)-[restful](https://xugaoxiang.com/tag/restful/) 0.3.8

### 简介

前面我们讲到`flask`路由的时候，可以通过`app.route`来指定`HTTP`的请求方法(`GET`、`POST`、`PUT`、`DELETE`等)，并在请求函数中根据不同的请求方法，执行不同的业务逻辑。这样就已经实现一个简单的`Restful`请求了。但是在`flask`中有更好的方法来实现，那就是`flask-restful`扩展了。

`RESTful`架构风格规定，数据的元操作，即CRUD(即数据的增删查改)操作，分别对应于`HTTP`方法，`GET`用来获取资源，`POST`用来新建资源(也可以用于更新资源)，`PUT`用来更新资源，`DELETE`用来删除资源，这样就统一了数据操作的接口，仅仅通过`HTTP`方法，就可以完成对数据的增删查改工作。

### 安装flask-[restful](https://xugaoxiang.com/tag/restful/)

常规操作，通过`pip`安装

```
pip install flask-restful
```

### flask-restful基本使用

插件安装好后，就可以导入模块了，看下面的示例

```python
from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse

USERS = [
    {"name": "zhangsan"},
    {"name": "lisi"},
    {"name": "wangwu"},
    {"name": "zhaoliu"}
]

class Users(Resource):
    def get(self):
        return jsonify(USERS)

    def post(self):
        args = reqparse.RequestParser() \
            .add_argument('name', type=str, location='json', required=True, help="名字不能为空") \
            .parse_args()

        if args['name'] not in USERS:
            USERS.append({"name": args['name']})

        return jsonify(USERS)

    def delete(self):
        USERS = []
        return jsonify(USERS)


app = Flask(__name__)
api = Api(app, default_mediatype="application/json")

api.add_resource(Users, '/users')

app.run(host='0.0.0.0', port=5001, use_reloader=True)
```

`flask-restful`扩展通过`api.add_resource()`方法来添加路由，方法的第一个参数是一个类名，该类继承`Resource`基类，其成员方法定义了不同的`HTTP`请求方法的逻辑；第二个参数定义了`URL`路径。在`Users`类中，我们分别实现了`get`、`post`、`delete`方法，分别对应`HTTP`的`GET`、`POST`、`DELETE`请求。

另外，**`flask-restful`还提供了`argparse`，它可以方便地实现对`http`请求中客户端发送过来的数据进行校验处理**，这有点像表单中的验证方法，在实际项目中非常实用。



程序启动以后，我们访问 `http://127.0.0.1:5001/users`，`GET`请求时会给出`USERS`的内容、`POST`请求时会在`USERS`中添加一项(如果不存在)并返回`USERS`更新后的内容。`DELETE`请求则清空`USERS`并返回空。

客户端部分，我们使用`postman`来模拟请求

![flask-restful-get](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F9347a48143ebac59-733ffe.png)

![flask-restful-post](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F59a37ac144fbbd22-e9f1b2.png)

![flask-restful-delete](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F3f32ddabdba3ba9e-93e63d.png)

### GET方法中如何获取参数

针对每个用户名，我们写个类，同样继承自`Resource`，在`get`方法中，接收参数`userid`，简单起见，`userid`定义为该用户名在`USERS`列表中的索引

```python
class UserId(Resource):
    def get(self, userid):
        return jsonify(
            {"name": USERS[int(userid)].get("name")}
        )

api.add_resource(UserId, '/user/<userid>')
```

在`api.add_resource()`方法中，第二个参数`/user/<userid>`中的`<userid>`，就是用户传递过来的参数，这点写法上跟`flask`路由的写法是一模一样的。程序启动后，访问 `http://127.0.0.1:5001/user/0` 获取的就是`USERS`列表中第一个用户的信息

![flask-restful-get-param](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F67654e4fb6e58040-52aec1.png)

### 在flask-restful中添加日志

[Flask教程(十五)日志](https://xugaoxiang.com/2020/08/25/flask-15-logging/) 已经提过如何在`flask`中使用日志功能。在`flask-restful`中，`logger`的使用有更优雅的方式，来看示例

```python
import logging.config
from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "simple",
                "stream": "ext://sys.stdout",
            },
            "info_file_handler": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "simple",
                "filename": "info.log",
                "maxBytes": 10485760,
                "backupCount": 50,
                "encoding": "utf8",
            },
            "error_file_handler": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "simple",
                "filename": "errors.log",
                "maxBytes": 10485760,
                "backupCount": 20,
                "encoding": "utf8",
            },
            "debug_file_handler": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "simple",
                "filename": "debug.log",
                "maxBytes": 10485760,
                "backupCount": 50,
                "encoding": "utf8",
            },
        },
        "loggers": {
            "my_module": {"level": "ERROR", "handlers": ["console"], "propagate": "no"}
        },
        "root": {
            "level": "DEBUG",
            "handlers": ["error_file_handler", "debug_file_handler"],
        },
    }
)

USERS = [
    {"name": "zhangsan"},
    {"name": "lisi"},
    {"name": "wangwu"},
    {"name": "zhaoliu"}
]

class Users(Resource):
    def __init__(self, **kargs):
        self.logger = kargs.get('logger')

    def get(self):
        return jsonify(USERS)

    def post(self):
        args = reqparse.RequestParser() \
            .add_argument('name', type=str, location='json', required=True, help="名字不能为空") \
            .parse_args()

        self.logger.debug(args)

        if args['name'] not in USERS:
            USERS.append({"name": args['name']})

        return jsonify(USERS)

    def delete(self):
        USERS = []
        return jsonify(USERS)


app = Flask(__name__)
api = Api(app, default_mediatype="application/json")

api.add_resource(Users, '/users', resource_class_kwargs={
    "logger": logging.getLogger('/Users')
})

app.run(host='0.0.0.0', port=5001, use_reloader=True)
```

我们使用上次用到的`dictConfig`，主要的区别在于`api.add_resource()`方法中，使用了参数`resource_class_kwargs`，然后在`Resource`子类中的构造函数`__init__`，将日志记录器获取到，后面就可以在各个处理方法中使用了。再次使用`postman`发起`POST`请求，可以看到`debug.log`是这个样子的

![flask-restful-logging](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F807c773888c3a3ac-bd78fa.png)