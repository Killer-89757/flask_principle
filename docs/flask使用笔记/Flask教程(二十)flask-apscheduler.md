# Flask教程(二十)flask-apscheduler

### 软硬件环境

- windows 10 64bit
- anaconda3 with [python](https://xugaoxiang.com/tag/python/) 3.7
- pycharm 2020.1.2
- [flask](https://xugaoxiang.com/tag/flask/) 1.1.2
- [flask](https://xugaoxiang.com/tag/flask/)-[apscheduler](https://xugaoxiang.com/tag/apscheduler/) 1.11.0

### 前言

前文 [Python实用模块之`apscheduler`](https://xugaoxiang.com/2020/07/17/python-module-apscheduler) 已经介绍过`apscheduler`的基本使用了。`flask-apscheduler`将`apscheduler`移植到了`flask`应用中，使得在`flask`中可以非常方便的使用定时任务了，除此之外，它还有如下几个特性

- 根据`Flask`配置加载调度器配置
- 根据`Flask`配置加载任务调度器
- 允许指定服务器运行任务
- 提供`RESTful API`管理任务，也就是远程管理任务
- 为`RESTful API`提供认证

### 使用示例

在使用之前，我们需要安装这个模块，使用`pip`

```python
pip install flask-apscheduler
```

`flask-apscheduler`的相关配置，我们会将它和其它扩展一起，放在应用的配置里，下面先来看个间隔定时任务

```python
from flask import Flask
from flask_apscheduler import APScheduler

class Config(object):
    JOBS = [
        {
            'id': 'job1',
            'func': 'run:add',
            'args': (1, 2),
            'trigger': 'interval',
            'seconds': 3
        }
    ]

    SCHEDULER_API_ENABLED = True


def add(a, b):
    print(a+b)


if __name__ == '__main__':
    app = Flask(__name__)
    app.config.from_object(Config())

    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    app.run()
```

在`Config`类里，有一个列表`JOBS`，每个元素是一项任务，上面的示例代码中只有一个任务，是一个`interval`任务，每3秒执行一次，具体执行的任务方法是`add`，接收2个参数。`func`后面的值格式是 模块名:方法名

在`flask app`实例化后，运行之前，我们进行`flask-apscheduler`的初始化，这一步必不可少

```python
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
```

执行上面的工程，我们可以得到

```python
(FlaskTutorial) D:\xugaoxiang\FlaskTutorial\Flask-20-apscheduler>python run.py
 * Serving Flask app "run" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
3
3
3
```

上边我们设置了`SCHEDULER_API_ENABLED = True`，可以通过访问 http://127.0.0.1:5000/scheduler ，其中`scheduler`是默认的`RESTful API`前缀

![flask-apscheduler](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fabd51b3231864f2b-88f1a6.png)

通过查看源码文件`scheduler.py`，我们可以看到`flask-apscheduler`为我们提供了哪些`RESTful API`

```python
    def _load_api(self):
        """
        Add the routes for the scheduler API.
        """
        self._add_url_route('get_scheduler_info', '', api.get_scheduler_info, 'GET')
        self._add_url_route('add_job', '/jobs', api.add_job, 'POST')
        self._add_url_route('get_job', '/jobs/<job_id>', api.get_job, 'GET')
        self._add_url_route('get_jobs', '/jobs', api.get_jobs, 'GET')
        self._add_url_route('delete_job', '/jobs/<job_id>', api.delete_job, 'DELETE')
        self._add_url_route('update_job', '/jobs/<job_id>', api.update_job, 'PATCH')
        self._add_url_route('pause_job', '/jobs/<job_id>/pause', api.pause_job, 'POST')
        self._add_url_route('resume_job', '/jobs/<job_id>/resume', api.resume_job, 'POST')
        self._add_url_route('run_job', '/jobs/<job_id>/run', api.run_job, 'POST')
```

它们的使用方法是这样的，比如我要查看当前应用中的所有任务，可以访问使用`GET`方法访问 http://127.0.0.1:5000/scheduler/jobs

![flask-apscheduler](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Faacbf2078564d091-5136f6.png)

如果不习惯使用配置的话，还可以使用装饰器的方式，来看下面的示例

```python
from flask import Flask
from flask_apscheduler import APScheduler


class Config(object):
    SCHEDULER_API_ENABLED = True


scheduler = APScheduler()


@scheduler.task('interval', id='do_job_1', seconds=30)
def job1():
    print('Job 1 executed')


# cron examples
@scheduler.task('cron', id='do_job_2', minute='*')
def job2():
    print('Job 2 executed')


@scheduler.task('cron', id='do_job_3', week='*', day_of_week='sun')
def job3():
    print('Job 3 executed')


if __name__ == '__main__':
    app = Flask(__name__)
    app.config.from_object(Config())

    scheduler.init_app(app)
    scheduler.start()

    app.run()
```

最后再来看个复杂点的配置

```python
class Config(object):
    JOBS = [
        {
            'id': 'job1',
            'func': 'run:job1',
            'args': (1, 2),
            'trigger': 'interval',
            'seconds': 10
        }
    ]

    SCHEDULER_JOBSTORES = {
        'default': SQLAlchemyJobStore(url='sqlite://')
    }

    SCHEDULER_EXECUTORS = {
        'default': {'type': 'threadpool', 'max_workers': 20}
    }

    SCHEDULER_JOB_DEFAULTS = {
        'coalesce': False,
        'max_instances': 3
    }

    SCHEDULER_API_ENABLED = True
```

其中`SCHEDULER_JOBSTORES`指的就是作业存储器，我们把它存储到`sqlite`中。`SCHEDULER_EXECUTORS`指的是执行器的配置，使用的类型是`threadpool`线程池，且设置最大线程数为20。`SCHEDULER_JOB_DEFAULTS`是任务的一些配置，其中

- coalesce指的是当由于某种原因导致某个任务积攒了好多次没有实际运行(比如说系统挂了2分钟后恢复，比如`supervisor`的进程监控工具，有一个任务是每分钟跑一次的，按道理说这2分钟内本来是计划要运行2次的，但实际没有执行），如果`coalesce`为`True`

  ，下次这个任务被执行时，只会执行1次，也就是最后这次，如果为`False`，那么会执行2次

- max_instance就是说同一个任务同一时间最多有几个实例在跑`SCHEDULER_API_ENABLED`指定是否开启`API`

除了上面的常用配置之外，还有一些

```python
SCHEDULER_TIMEZONE          # 配置时区
SCHEDULER_API_PREFIX        # 配置API路由前缀
SCHEDULER_ENDPOINT_PREFIX   # 配置API路由后缀
SCHEDULER_ALLOWED_HOSTS     # 配置访问白名单
SCHEDULER_AUTH              # 配置认证中心
```

在服务器上部署`flask`应用的时候，经常需要设置时区，否则会报错

```python
class Config(object):
    SCHEDULER_TIMEZONE = 'Asia/Shanghai'
```

配置`RESTful API`路由的前缀和后缀

```python
class Config(object):
    SCHEDULER_API_PREFIX ='/waws'
```

那么访问所有任务的路由就会由原来的 http://127.0.0.1:5000/scheduler/jobs 变成 http://127.0.0.1:5000/waws/jobs

如果需要设定只允许某些主机访问的话，可以设置白名单，如果是允许全部的话，也可以写上`*`

```
class Config(object):
    SCHEDULER_ALLOWED_HOSTS = ['waws.com']
```

如果要添加认证的话，可以这样实现

```python
from flask import Flask
from flask_apscheduler import APScheduler
from flask_apscheduler.auth import HTTPBasicAuth


class Config(object):
    JOBS = [
        {
            'id': 'job1',
            'func': 'run2:add',
            'args': (1, 2),
            'trigger': 'interval',
            'seconds': 3
        }
    ]

    SCHEDULER_API_ENABLED = True
    SCHEDULER_AUTH = HTTPBasicAuth()


def add(a, b):
    print(a+b)


if __name__ == '__main__':
    app = Flask(__name__)
    app.config.from_object(Config())

    scheduler = APScheduler()
    # it is also possible to set the authentication directly
    # scheduler.auth = HTTPBasicAuth()
    scheduler.init_app(app)
    scheduler.start()

    @scheduler.authenticate
    def authenticate(auth):
        return auth['username'] == 'guest' and auth['password'] == 'guest'

    app.run()
```

在访问`scheduler`之前，先做一次认证，如果满足条件，如上面通过`http`请求传递过来的参数`username=guest`且`password=guest`，就可以继续访问，否则拒绝访问。