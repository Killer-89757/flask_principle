#  flask03

```python
import pymysql
from dbutils.pooled_db import PooledDB

class SqlHelper(object):
    def __init__(self):
        self.pool = PooledDB(
            creator=pymysql,  # 使用链接数据库的模块
            maxconnections=6,  # 连接池允许的最大连接数，0和None表示不限制连接数
            mincached=2,  # 初始化时，链接池中至少创建的链接，0表示不创建
            blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
            ping=0,
            # ping MySQL服务端，检查是否服务可用。# 如：0 = None = never, 1 = default = whenever it is requested, 2 = when a cursor is created, 4 = when a query is executed, 7 = always
            host='127.0.0.1',
            port=3306,
            user='root',
            password='111111',
            database='cat_12',
            charset='utf8'
        )

    def open(self):
        conn = self.pool.connection()
        cursor = conn.cursor()
        return conn,cursor

    def close(self,cursor,conn):
        cursor.close()
        conn.close()

    def fetchall(self,sql, *args):
        """ 获取所有数据 """
        conn,cursor = self.open()
        cursor.execute(sql, args)
        result = cursor.fetchall()
        self.close(conn,cursor)
        return result

    def fetchone(self,sql, *args):
        """ 获取所有数据 """
        conn, cursor = self.open()
        cursor.execute(sql, args)
        result = cursor.fetchone()
        self.close(conn, cursor)
        return result

    def __enter__(self):
        return self.open()[1]

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(exc_type, exc_val, exc_tb)       # None None None
        


db = SqlHelper()

# 在这个部分存在问题，退出的时候不能干掉conn,course
with db as cur:
    cur.execute('xxxx')
```

## 今日概要

- wsgi
- 创建flask对象
  - 模板
  - 静态文件
- 路由系统
  - 路由的应用：装饰器（推荐）、方法
  - 动态路由
- 视图
  - FBV
  - CBV
- 模板
  - 继承
  - include
  - 自定义标签
- 特殊装饰器
  - before_request充当中间件角色

## 今日详细

### 1.wsgi 找源码的流程

```python
from werkzeug.serving import run_simple
from werkzeug.wrappers import Response

def func(environ, start_response):
    print('请求来了')
    response = Response('你好')
    return response(environ, start_response)


if __name__ == '__main__':
    run_simple('127.0.0.1', 5000, func)
```

```python
"""
    1.程序启动，等待用户请求到来
        app.run()
    2.用户请求到来 app()    
        app.__call__
"""

from flask import Flask

app = Flask(__name__)

@app.route('/index')
def index():
    return 'hello world'

if __name__ == '__main__':
    app.run()
```

![image-20240504110244520](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504110244520-b185db.png)

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504110508736-014838.png)

![](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504111147374-9a61d0.png)

![image-20240504111838917](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504111838917-b52c02.png)

![image-20240504112504068](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504112504068-7bf78b.png)

> **追踪过程如下：**
>
> **app.run()---> run_simple()中的self == app()---> `__call__` --->  wsgi_app()---> full_dispatch_request()----> finalize_request(rv)---->make_response(rv)----> response_class()--->Response(ResponseBase)----> from werkzeug.wrappers import Response as ResponseBase**

![image-20240504112031694](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504112031694-a9dca0.png)

### 2.flask对象

静态文件的处理。

![image-20240504114341659](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504114341659-9601fe.png)

![image-20240504102524366](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504102524366-a53c89.png)

推荐

```python
from flask import Flask,render_template

app = Flask(__name__,template_folder='templates',static_folder='static')

@app.route('/index')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()
```

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>
    <h1>首页</h1>
    <img src="/static/xx/xx/mm.jpg" />
    
    <!-- 建议 -->
    <img src="{{ url_for('static',filename='xx/xx/mm.jpg')}}" />
</body>
</html>
```

> 推荐使用这种格式的原因：`<img src="{{ url_for('static',filename='xx/xx/mm.jpg')}}" />`
>
> 当我们的static目录变成其他名字，可以不用修改源代码，自动变化去寻找文件
>
> ![image-20240504114938519](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504114938519-7d8027.png)

### 3.配置文件

#### 3.1 基于全局变量

```python
from flask import Flask,render_template

app = Flask(__name__)

# 加载配置文件
app.config.from_object('config.settings')

print(app.config['DB_HOST'])

@app.route('/index')
def index():
    return 'index'

if __name__ == '__main__':
    app.run()
    

# settings.py
try:
    from .localsettings import *
except ImportError:
    pass

# localsettings.py
DB_HOST = '127.0.0.1'
DB_USER = 'root'
DB_PWE = '111111'
```

![image-20240504102711008](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504102711008-936c2a.png)

![image-20240504115832386](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504115832386-acb1b9.png)

#### 3.2 基于类的方式

![image-20240504102649494](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504102649494-f4718c.png)

### 4.路由系统

![image-20240504132850032](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504132850032-d0cfc4.png)

![image-20240504134401323](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504134401323-65be49.png)

细节部分代码展示

![image-20240504135559658](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504135559658-303747.png)

在看Rule、Map对象的细节

![image-20240504141042036](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504141042036-968037.png)

![image-20240504141537902](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504141537902-753f38.png)

![image-20240504142203005](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504142203005-da95e4.png)

- 路由的两种写法

  ```python
  def index():
      return render_template('index.html')
  app.add_url_rule('/index', 'index', index)
  
  # 公司里一般用这种方式
  @app.route('/login')
  def login():
      return render_template('login.html')
  ```

- 路由加载的源码流程

  ```python
  - 将url和函数打包成为 rule 对象
  - 将rule对象添加到map对象中。
  - app.url_map = map对象
  ```

- 动态路由

  ```python
  @app.route('/login')
  def login():
      return render_template('login.html')
      
  @app.route('/login/<name>')
  def login(name):
  	print(type(name))
      return render_template('login.html')
      
  @app.route('/login/<int:name>')
  def login(name):
  	print(type(name))
      return render_template('login.html')
  ```

- 支持正则表达式的路由

  ```python
  from flask import Flask, render_template
  
  app = Flask(__name__)
  
  from werkzeug.routing import BaseConverter
  
  
  class RegConverter(BaseConverter):
      def __init__(self, map, regex):
          super().__init__(map)
          self.regex = regex
  
      # 对匹配到的值进行处理的函数(父类中有)
      def to_python(self, value):
          # return value  默认匹配得到的是字符串
          return int(value)  # 将其变成数值型
  
  app.url_map.converters['regex'] = RegConverter
  
  @app.route('/index/<regex("\d+"):x1>')
  def index(x1):
      print(x1, type(x1))     # 1 <class 'int'>
      return render_template('index.html')
  
  
  if __name__ == '__main__':
      app.run()
  ```


![image-20240504144341724](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504144341724-eec891.png)

![image-20240504143321430](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504143321430-896100.png)

![image-20240504144435291](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504144435291-0ed6eb.png)

### 5.视图

#### 5.1 FBV

```python
def index():
    return render_template('index.html')
app.add_url_rule('/index', 'index', index)


# 公司里一般用这种方式
@app.route('/login')
def login():
    return render_template('login.html')
```

#### 5.2 CBV

```python
from flask import Flask,render_template,views

app = Flask(__name__,)

def test1(func):
    def inner(*args,**kwargs):
        print('before1')
        result = func(*args,**kwargs)
        print('after1')
        return result
    return inner

def test2(func):
    def inner(*args,**kwargs):
        print('before2')
        result = func(*args,**kwargs)
        print('after2')
        return result
    return inner


class UserView(views.MethodView):
    methods = ['GET',"POST"]

    decorators = [test1,test2]


    def get(self):
        print('get')
        return 'get'

    def post(self):
        print('post')
        return 'post'

app.add_url_rule('/user', view_func=UserView.as_view('user')) # endpoint

if __name__ == '__main__':
    app.run()
```

![image-20240504145247964](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504145247964-38090f.png)

![image-20240504160841635](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504160841635-8bd59c.png)

![image-20240504161003227](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504161003227-f5a9c5.png)

### 6.模板

#### 6.1 基本用法

flask比django更加接近Python。 

```python
from flask import Flask,render_template

app = Flask(__name__,)

def func(arg):
    return '你好' + arg

@app.route('/md')
def index():
    nums = [11,222,33]
    return render_template('md.html',nums=nums,f=func)


if __name__ == '__main__':
    app.run()
```

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>
    <h1>头</h1>
        {% block content %} {% endblock %}
    <h1>底</h1>
</body>
</html>
```


```html
<form action="">
    <input type="text">
    <input type="text">
    <input type="text">
    <input type="text">
    <input type="text">
</form>
```


```html
{% extends 'layout.html' %}


{% block content %}
    <h1>MD</h1>
    {% include 'form.html' %}
    {{ f("waws") }}
{% endblock %}
```

#### 6.2 定义全局模板方法

```python
from flask import Flask,render_template

app = Flask(__name__,)

@app.template_global() #  {{ func("waws") }}
def func(arg):
    return '海狗子' + arg

@app.template_filter() # {{ "waws"|x1("killer") }} waws默认作为x1的第一个参数arg、在x1()中的参数使用name进行接收
def x1(arg,name):
    return '海狗子' + arg + name

@app.template_filter() # {{ "waws"|x1() }}
def x2(arg):
    return '海狗子' + arg


@app.route('/md/hg')
def index():
    return render_template('md_hg.html')

if __name__ == '__main__':
    app.run()
```

注意：在蓝图中注册时候，应用返回只有本蓝图。

![image-20240504163746298](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504163746298-cca7a5.png)

### 7.特殊装饰器

```python
from flask import Flask,render_template,request

app = Flask(__name__)

@app.before_request
def f1():
    if request.path == '/login':
        return
    print('f1')
    # return '123'

@app.after_request
def f10(response):       # 注意在after_request中参数和返回值都是response
    print('f10')
    return response

@app.route('/index')
def index():
    print('index')
    return render_template('index.html')

if __name__ == '__main__':
    app.run()
```

![image-20240504165246679](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504165246679-81aac4.png)

多个装饰器

```python
from flask import Flask,render_template,request

app = Flask(__name__)

@app.before_request
def f1():
    print('f1')

@app.before_request
def f2():
    print('f2')

@app.after_request
def f10(response):
    print('f10')
    return response

@app.after_request
def f20(response):
    print('f20')
    return response

@app.route('/index')
def index():
    print('index')
    return render_template('index.html')

if __name__ == '__main__':
    app.run()
    app.__call__   
```

注意：before_after request可以在蓝图中定义，在蓝图中定义的话，作用域只在本蓝图。

![image-20240504165800817](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504165800817-2371b1.png)

![image-20240504170120835](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504170120835-63e63a.png)

![image-20240504170316904](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504170316904-e4dcd5.png)

维护before_request和after_request的列表

![image-20240504170507051](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504170507051-53910a.png)

![image-20240504170551893](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504170551893-ed9e94.png)

### 8.特殊装饰器的另一种使用方式

```python
from flask import Flask,render_template

app = Flask(__name__,)

@app.route('/index')
def index():
    return render_template('index.html')


@app.before_request
def func():
    print('xxx')

def x1():
    print('xxx')
app.before_request(x1)

if __name__ == '__main__':
    app.run()
```

## 赠送：threading.local

```python
import time
import threading

class Foo(object):
    def __init__(self):
        self.num = 0

val2 = Foo()

def task(i):
    val2.num = i
    time.sleep(1)
    print(val2.num)

for i in range(4):
    t = threading.Thread(target=task,args=(i,))
    t.start()
```

![image-20240504172025070](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504172025070-b92fae.png)

```python
import time
import threading

# 当每个线程在执行 val1.xx=1 ，在内部会为此线程开辟一个空间，来存储 xx=1
# val1.xx,找到此线程自己的内存地址去取自己存储 xx
# 其实就是通过线程ID进行标记
val1 = threading.local()

def task(i):
    val1.num = i
    time.sleep(1)
    print(val1.num)

for i in range(4):
    t = threading.Thread(target=task,args=(i,))
    t.start()
```

![image-20240504172225291](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504172225291-6d777e.png)