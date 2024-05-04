# flask04

1. wsgi

   ```
   django和flask内部都没有实现socket，而是wsgi实现。
   wsgi是web服务网管接口，他是一个协议，实现它的协议的有：wsgiref/werkzurg/uwsgi
   ```

   ```python
   # django之前
   from wsgiref.simple_server import make_server
    
   def run(environ, start_response):
       start_response('200 OK', [('Content-Type', 'text/html')])
       return [bytes('<h1>Hello, web!</h1>', encoding='utf-8'), ]
    
   if __name__ == '__main__':
       httpd = make_server('127.0.0.1', 8000, run)
       httpd.serve_forever()
   ```


## 概要

- flask上下文源码
- flask的扩展

## 内容详细

### 1. 栈

后进先出，通过列表可以实现一个栈

```python
v = [11,22,33]
v.append(44)
v.pop()
```

应用场景：

- 节流

### 2. 面向对象

```python
class Foo(object):

    def __setattr__(self, key, value):
        print("__setattr__执行")
        print(key,value)
    
    def __getattr__(self, item):
        print("__getattr__执行")
        print(item)

obj = Foo()
obj.x = 123
obj.x

"""
__setattr__执行
x 123
__getattr__执行
x
"""
```

- drf中request

  ```python
  request.data
  request.query_params
  request._request
  request._request.POST
  request._request.GET
  
  #
  request.data
  request.query_params
  request.POST
  request.Data
  ```

  实现方式如下

  ![image-20240504182809130](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504182809130-e29fbf.png)

```python
class Local(object):
    def __init__(self):
        # self.storage = {}
        object.__setattr__(self,"storage",{})

    def __setattr__(self, key, value):
        self.storage[key] = value

    def __getattr__(self, item):
        return self.storage.get(item)

local = Local()
local.x1 = 123
print(local.x1)
```

![image-20240504183924097](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504183924097-af9395.png)

![image-20240504192827539](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504192827539-00960c.png)

```python
# 通过下面的代码更清晰直观的了解.点的特性
class ClassA(object):

    def __init__(self, classname):
        self.classname = classname

    def __getattr__(self, attr):
        return('invoke __getattr__', attr)

insA = ClassA('ClassA')
print(insA.__dict__) # 实例insA已经有classname属性了
# {'classname': 'ClassA'}

print(insA.classname) # 不会调用__getattr__
# ClassA

print(insA.grade) # grade属性没有找到，调用__getattr__
# ('invoke __getattr__', 'grade')
```

### 3.线程唯一标识

```python
import threading
from threading import get_ident

def task():
    ident = get_ident()
    print(ident)
    
for i in range(20):
    t = threading.Thread(target=task)
    t.start()
```

### 4.自定义threading.local

```python
import threading
"""
storage = {
    1111:{'x1':[0,1,2,3]},
    1112:{'x1':1}
    1113:{'x1':2}
    1114:{'x1':3}
    1115:{'x1':4}
}
"""
class Local(object):
    def __init__(self):
        object.__setattr__(self,'storage',{})

    def __setattr__(self, key, value):
        ident = threading.get_ident()
        if ident in self.storage:
            self.storage[ident][key] = value
        else:
            self.storage[ident] = {key:value}

    def __getattr__(self, item):
        ident = threading.get_ident()
        if ident not in self.storage:
            return
        return self.storage[ident].get(item)

local = Local()

def task(arg):
    local.x1 = arg
    print(local.x1)

for i in range(5):
    t = threading.Thread(target=task,args=(i,))
    t.start()
```

### 5.加强版threading.local

```python
import threading
"""
storage = {
    1111:{'x1':[]},
    1112:{'x1':[]}
    1113:{'x1':[]}
    1114:{'x1':[]}
    1115:{'x1':[]},
    1116:{'x1':[]}
}
"""
class Local(object):
    def __init__(self):
        object.__setattr__(self,'storage',{})

    def __setattr__(self, key, value):
        ident = threading.get_ident()
        if ident in self.storage:
            self.storage[ident][key].append(value)
        else:
            self.storage[ident] = {key:[value,]}

    def __getattr__(self, item):
        ident = threading.get_ident()
        if ident not in self.storage:
            return
        return self.storage[ident][item][-1]

local = Local()

def task(arg):
    local.x1 = arg
    print(local.x1)

for i in range(5):
    t = threading.Thread(target=task,args=(i,))
    t.start()
```

### 6.flask源码关于local的实现(`核心`)

```python
try:
    # 协程
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        # 线程
        from thread import get_ident
    except ImportError:
        from _thread import get_ident
"""
__storage__ = {
    1111:{"stack":[waws] }
}
"""
class Local(object):

    def __init__(self):
        # self.__storage__ = {}
        # self.__ident_func__ = get_ident
        object.__setattr__(self, "__storage__", {})
        object.__setattr__(self, "__ident_func__", get_ident)

    def __iter__(self):
        return iter(self.__storage__.items())

    def __release_local__(self):
        self.__storage__.pop(self.__ident_func__(), None)

    def __getattr__(self, name):
        try:
            return self.__storage__[self.__ident_func__()][name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        ident = self.__ident_func__() # 1111
        storage = self.__storage__
        try:
            storage[ident][name] = value
        except KeyError:
            storage[ident] = {name: value}

    def __delattr__(self, name):
        try:
            del self.__storage__[self.__ident_func__()][name]
        except KeyError:
            raise AttributeError(name)

class LocalStack(object):
    def __init__(self):
        self._local = Local()

    def push(self, obj):
        """Pushes a new item to the stack"""
        # self._local.stack ----  __getattr__
        # rv = None
        rv = getattr(self._local, "stack", None)
        if rv is None:
            # self._local.stack = [] -----> __setattr__ ----> Local().__storage__ = {thread_id:{'stack':[]}}
            self._local.stack = rv = []
        rv.append(obj)   # Local().__storage__ = {thread_id:{'stack':["waws"]}}
        return rv

    def pop(self):
        # getattr(self._local, "stack", None) ==》等价于 self._local.stack
        # 因为.stack,没有stack,走__getattr__,self.__storage__[self.__ident_func__()][name]，
        # 就拿到了self.__storage__[thread_id]['stack'],在取self.__storage__[thread_id]['stack'][-1]
        # or self.__storage__[thread_id]['stack'].pop()
        stack = getattr(self._local, "stack", None)
        if stack is None:
            return None
        elif len(stack) == 1:
            # release_local(self._local)
            # del __storage__[1111]
            return stack[-1]
        else:
            return stack.pop()

    @property
    def top(self):
        try:
            # 因为.stack,没有stack,走__getattr__,self.__storage__[self.__ident_func__()][name]，
            # 就拿到了self.__storage__[thread_id]['stack'],在取self.__storage__[thread_id]['stack'][-1]
            return self._local.stack[-1]
        except (AttributeError, IndexError):
            return None

obj = LocalStack()
obj.push('waws')
obj.push('killer')

print(obj.top)

obj.pop()
obj.pop()
```

总结：

```python
在flask中有个local类，他和threading.local的功能一样，为每个线程开辟空间进行存取数据，他们两个的内部实现机制，内部维护一个字典，以线程(协程)ID为key，进行数据隔离，如：
    __storage__ = {
		1211:{'k1':123}
    }
    
    obj = Local()
    obj.k1 = 123
    
在flask中还有一个LocalStack的类，他内部会依赖local对象，local对象负责存储数据，localstack对象用于将local中的值维护成一个栈。
	__storage__ = {
		1211:{'stack':['k1',]}
    }

	obj= LocalStack()
    obj.push('k1')
    obj.top
    obj.pop()
```

- [ ] TODO：在TOP中`return stack[-1]` 是如何从`__storage__`删除整个数据的

7. flask源码中总共有2个localstack对象

> 在最新的flask 3.0.3版本中这个部分不同，回退和老师相同版本 flask == 1.1.1

```python
# context locals
__storage__ = {
	1111:{'stack':[RequestContext(reqeust,session),]},
    1123:{'stack':[RequestContext(reqeust,session),]},
}
_request_ctx_stack = LocalStack()


__storage__ = {
	1111:{'stack':[AppContenxt(app,g),]}
    1123:{'stack':[AppContenxt(app,g),]},
}
_app_ctx_stack = LocalStack()
```

```python
_request_ctx_stack.push('waws')
_app_ctx_stack.push('killer')
```

- 上下文管理
  - 请求上下文管理
  - 应用上下文管理

![image-20240504205501257](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504205501257-4b01dd.png)

### 7.源码初识

#### 7.1 项目启动

- 实例化Flask对象

  ```
  app = Flask(__name__)
  ```

  ```python
  1. 对app对象封装一些初始化的值。
  	app.static_url_path
  	app.static_folder
  	app.template_folder
  	app.view_functions = {}
  2. 添加静态文件的路由
      self.add_url_rule(
          self.static_url_path + "/<path:filename>",
          endpoint="static",
          host=static_host,
          # 添加静态文件的路由,这个在前面url_map的那个地方见过
          view_func=self.send_static_file,
          )
          
  3. 实例化了url_map的对象，以后在map对象中放 【/index/ 函数的对象应观】
      class Flask(object):
          url_rule_class = Rule
          url_map_class = Map
  
          def __init__(self...):
              self.static_url_path
              self.static_folder
              self.template_folder
              self.view_functions = {}
              self.url_map = self.url_map_class()
      app = Flask()
      app.view_functions
  app.url_rule_class
  ```

- 加载配置文件（给app的config进行赋值）

  ```python
  from flask import Flask
  
  app = Flask(__name__,static_url_path='/xx')
  
  # app.config =  Config对象
  # Config对象.from_object('xx.xx')
  # 通过 app.config 拿到配置项
  app.config.from_object('xx.xx')
  
  # config.py
  def from_object(self, obj):
      if isinstance(obj, string_types):
          obj = import_string(obj)
      for key in dir(obj):
          if key.isupper():
              self[key] = getattr(obj, key) 
  ```

  ```python
  1. 读取配置文件中的所有键值对，并将键值对全都放到Config对象。（Config是一个字典）
  2. 把包含所有配置文件的Config对象，赋值给 app.config
  ```

  ![image-20240504211346069](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504211346069-e5edcf.png)

- 添加路由映射

  ```python
  from flask import Flask
  
  app = Flask(__name__,static_url_path='/xx')
  
  @app.route('/index')
  def index():
      return 'hello world'
  ```

  ```python
  1. 将 url = /index  和  methods = [GET,POST]  和 endpoint = "index"封装到Rule对象
  
  2. 将Rule对象添加到 app.url_map中。
  
  3. 把endpoint和函数的对应关系放到 app.view_functions中。
  ```

  这个地方的细节可以看flask03中url和view_func的匹配关系

- 截止目前

  ```
  app.config
  app.url_map
  app.view_functions
  ```

- 运行flask

  ```python
  from flask import Flask
  
  app = Flask(__name__,static_url_path='/xx')
  
  @app.route('/index')
  def index():
      return 'hello world'
  
  if __name__ == '__main__':
      app.run()
  ```

  ```python
  1. 内部调用werkzeug的run_simple，内部创建socket，监听IP和端口，等待用户请求到来。
  
  2. 一旦有用户请求，执行app.__call__方法。
  
  	class Flask(object):
          def __call__(self,envion,start_response):
              pass
          def run(self):
  			run_simple(host, port, self, **options)
  
      if __name__ == '__main__':
          app.run()
  ```


## 扩展

```python
class Foo:
     # 

obj = Foo()
obj() # __call__

obj[x1] = 123 # __setitem__
obj[x2]  # __getitem__

obj.x1 = 123 # __setattr__
obj.x2  # __getattr__
```

SQLhelper

- 方式一

  - > 因为是连接池，每个连接都是独立的，当我们不使用self.local的时候，直接在__exit__的时候关闭连接，会导致假设两个连接，连接1和连接2，连接1先生成，进行查询(事件长)，连接2到来，此时的self.course和self.conn变成了连接2，当连接2查询完了，离开，直接close，连接1没完成，但是我们找不到连接1了，会出现问题
    >
    > - 不能使用下面的方式
    >
    > def \__enter__(): 
    >
    > ​       self.conn,self.course = self.open()
    >
    > 
    >
    > def \__exit__():
    >
    > ​      self.course.close()
    >
    > ​      self.conn.close()

  ```python
  import pymysql
  import threading
  from dbutils.pooled_db import PooledDB
  
  """
  storage = {
      1111:{'stack':[]}
  }
  """
  
  
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
          self.local = threading.local()
  
      def open(self):
          conn = self.pool.connection()
          cursor = conn.cursor()
          return conn, cursor
  
      def close(self, cursor, conn):
          cursor.close()
          conn.close()
  
      def fetchall(self, sql, *args):
          """ 获取所有数据 """
          conn, cursor = self.open()
          cursor.execute(sql, args)
          result = cursor.fetchall()
          self.close(conn, cursor)
          return result
  
      def fetchone(self, sql, *args):
          """ 获取所有数据 """
          conn, cursor = self.open()
          cursor.execute(sql, args)
          result = cursor.fetchone()
          self.close(conn, cursor)
          return result
  
      def __enter__(self):
          conn, cursor = self.open()
          rv = getattr(self.local, 'stack', None)
          if not rv:
              self.local.stack = [(conn, cursor), ]
          else:
              rv.append((conn, cursor))
              self.local.stack = rv
          return cursor
  
      def __exit__(self, exc_type, exc_val, exc_tb):
          rv = getattr(self.local, 'stack', None)
          if not rv:
              # del self.local.stack
              return
          conn, cursor = self.local.stack.pop()
          cursor.close()
          conn.close()
  
  
  db = SqlHelper()
  ```

  ```python
  from sqlhelper import db
  
  
  # db.fetchall(...)
  # db.fetchone(...)
  
  with db as c1:
      c1.execute('select 1')
      with db as c2:
          c1.execute('select 2')
      print(123)
  ```

  ![image-20240504214818913](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504214818913-1b66f7.png)

  ![image-20240504215743522](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504215743522-3c9955.png)

- 方式二

  ```python
  import pymysql
  from dbutils.pooled_db import PooledDB
  
  POOL = PooledDB(
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
  
  
  class SqlHelper(object):
      def __init__(self):
          self.conn = None
          self.cursor = None
  
      def open(self):
          conn = POOL.connection()
          cursor = conn.cursor()
          return conn, cursor
  
      def close(self):
          self.cursor.close()
          self.conn.close()
  
      def __enter__(self):
          self.conn, self.cursor = self.open()
          return self.cursor
  
      def __exit__(self, exc_type, exc_val, exc_tb):
          self.close()
  ```

  ```python
  # ################## 使用 ##################
  # 使用这个的方式其实就是多个对象，自己管理自己的conn和cursor
  with SqlHelper() as c1:
      c1.execute('select 1')
      with SqlHelper() as c2:
          c2.execute('select 2')
      print(666)
  
  with SqlHelper() as cursor:
      cursor.execute('select 1')
  
  with SqlHelper() as cursor:
      cursor.execute('select 1')
  ```
