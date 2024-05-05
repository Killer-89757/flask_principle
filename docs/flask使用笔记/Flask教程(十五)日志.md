# Flask教程(十五)日志

### 软硬件环境

- windows 10 64bit
- anaconda3 with [python](https://xugaoxiang.com/tag/python/) 3.7
- pycharm 2020.1.2
- [flask](https://xugaoxiang.com/tag/flask/) 1.1.2

### 简介

`flask`日志使用标准的`python logging`。所有与`flask`相关的消息都用`app.logger`来记录，同样的，这个日志记录器也可用于你自己的日志记录。

`logging`是`python`自带的系统模块，在 [`python`实用模块](https://xugaoxiang.com/category/python编程/python实用模块/) 板块，我们已经介绍过它的使用方法，不了解的童鞋可以去看看，链接是 https://xugaoxiang.com/2019/12/04/python-module-logging/

### 日志配置

在`flask`中，不用任何配置就可以使用`app.logger`，如下示例

```python
@app.route('/login', methods=['POST'])
def login():
    user = get_user(request.form['username'])

    if user.check_password(request.form['password']):
        login_user(user)
        app.logger.info(f'{user.username} logged in successfully.')
        return redirect(url_for('index'))
    else:
        app.logger.info(f'{user.username} failed to log in')
        abort(401)
```

默认情况下，`flask`会自动添加一个`StreamHandler`到`app.logger`。在请求过程中，它会写到由`WSGI`服务器指定的，保存在`environ['wsgi.errors']`变量中的日志流(通常是`sys.stderr`)中。在请求之外，则会记录到`sys.stderr`。

如果你对日志默认配置不太满意的话，可以自行设置。当想要为项目配置日志时，应当在创建应用对象之前进行配置。 如果晚了，那么`app.logger`就会成为缺省记录器。下面我们使用`logging.config.dictConfig`来配置日志，看示例

```python
from flask import Flask

import logging.config

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

app = Flask(__name__)
```

上面是一个将日志写入文件的配置示例，当日志文件大小大于`10M`后，就用一个新的文件来存放日志，总的日志文件数目是50个。`debug`的信息写入`debug.log`，`info`的信息写入`info.log`，`error`的信息写入`error.log`。日志中每一行的内容是这样的

```
{"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
```

各字段分别对应，日志时间 - 模块 - 日志等级 - 具体的日志内容

![flask-logging](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F9f543f9cec8b662a-e67259.png)