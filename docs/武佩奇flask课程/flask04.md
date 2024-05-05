# flask04(`重中之重`)

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

![twisted](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Ftwisted-1629d2.png)

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

- 准备before_request、after_request、before_first_request函数

  ```python
  """
  {
    None:[f1,f2,f3]
  }
  """
  self.before_request_funcs = {}
  self.after_request_funcs = {}
  self.before_first_request_funcs = []
  
  @setupmethod
  def before_request(self, f):
      # 就是收集函数
      self.before_request_funcs.setdefault(None, []).append(f)
      return f
  
  @setupmethod
  def after_request(self, f):
  	# 同上
      self.after_request_funcs.setdefault(None, []).append(f)
      return f
  
  @setupmethod
  def before_first_request(self, f):
      # 同上
      self.before_first_request_funcs.append(f)
      return f
  ```

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

#### 7.2 有用户请求到来

```python
# 有请求过来的话，直接调用__call__方法
def __call__(self, environ, start_response):
    return self.wsgi_app(environ, start_response)

# 核心代码
def wsgi_app(self, environ, start_response):
    ctx = self.request_context(environ)
    error = None
    try:
        try:
            ctx.push()
            response = self.full_dispatch_request()
        except Exception as e:
            error = e
            response = self.handle_exception(e)
        except:  # noqa: B001
            error = sys.exc_info()[1]
            raise
        return response(environ, start_response)
    finally:
        if self.should_ignore_error(error):
            error = None
            ctx.auto_pop(error)
```

> 用户请求进来发生了什么？
>
> - environ：请求携带的信息-----> 封装成Request对象、创建session数据 ----> 绑定到一起封装成 RequestContext对象 (LocalStack)
>
> ```python
> # environ的详细值 携带的就是请求信息
> {'wsgi.version': (1, 0), 'wsgi.url_scheme': 'http', 'wsgi.input': <_io.BufferedReader name=1020>, 'wsgi.errors': <_io.TextIOWrapper name='<stderr>' mode='w' encoding='utf-8'>, 'wsgi.multithread': True, 'wsgi.multiprocess': False, 'wsgi.run_once': False, 'werkzeug.server.shutdown': <function WSGIRequestHandler.make_environ.<locals>.shutdown_server at 0x00000286D6DE1670>, 'SERVER_SOFTWARE': 'Werkzeug/0.16.1', 'REQUEST_METHOD': 'GET', 'SCRIPT_NAME': '', 'PATH_INFO': '/login', 'QUERY_STRING': '', 'REQUEST_URI': '/login', 'RAW_URI': '/login', 'REMOTE_ADDR': '127.0.0.1', 'REMOTE_PORT': 12551, 'SERVER_NAME': '127.0.0.1', 'SERVER_PORT': '5000', 'SERVER_PROTOCOL': 'HTTP/1.1', 'HTTP_HOST': '127.0.0.1:5000', 'HTTP_CONNECTION': 'keep-alive', 'HTTP_SEC_CH_UA': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"', 'HTTP_SEC_CH_UA_MOBILE': '?0', 'HTTP_SEC_CH_UA_PLATFORM': '"Windows"', 'HTTP_UPGRADE_INSECURE_REQUESTS': '1', 'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36', 'HTTP_SEC_PURPOSE': 'prefetch;prerender', 'HTTP_PURPOSE': 'prefetch', 'HTTP_ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7', 'HTTP_SEC_FETCH_SITE': 'none', 'HTTP_SEC_FETCH_MODE': 'navigate', 'HTTP_SEC_FETCH_USER': '?1', 'HTTP_SEC_FETCH_DEST': 'document', 'HTTP_ACCEPT_ENCODING': 'gzip, deflate, br, zstd', 'HTTP_ACCEPT_LANGUAGE': 'zh-CN,zh;q=0.9', 'HTTP_COOKIE': 'SL_G_WPT_TO=eo; SL_GWPT_Show_Hide_tmp=1; SL_wptGlobTipTmp=1', 'werkzeug.request': <Request 'http://127.0.0.1:5000/login' [GET]>}
> ```
>
> - 获取app对象，创建g数据 ---->绑定到一起封装成 AppContext对象 (LocalStack)
> - 从RequestContext对象中的Request对象的url信息，在Map对象中找到endpoint，在view_functions中找到view
> - 执行before_request函数
> - 执行view函数
> - 执行after_request函数
> - 销毁ctx和app_ctx

1. 创建ctx = RequestContext对象，其内部封装了 Request对象和session数据。

```python
# ctx核心代码
class RequestContext():
    def __init__(self, app, environ, request=None, session=None):
        self.app = app
        if request is None:
            # 构建Request对象将environ进行封装
            request = app.request_class(environ)
        self.request = request
        self.url_adapter = None
        try:
            self.url_adapter = app.create_url_adapter(self.request)
        except HTTPException as e:
            self.request.routing_exception = e
        self.flashes = None
        # 创建session
        self.session = session
```



![image-20240504235219692](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504235219692-e8b47f.png)

最终我们看各种请求数据的调用方法：

![image-20240504235656928](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240504235656928-86f69b.png) 

```python
# ctx.push方法
    def push(self):
        # 第一次进来不用管
        top = _request_ctx_stack.top
        if top is not None and top.preserved:
            top.pop(top._preserved_exc)

        app_ctx = _app_ctx_stack.top
        if app_ctx is None or app_ctx.app != self.app:
            # app_ctx不存在，创建app_ctx
            app_ctx = self.app.app_context()
            # 将app_ctx放入到AppLocal中
            app_ctx.push()
            self._implicit_app_ctx_stack.append(app_ctx)
        else:
            self._implicit_app_ctx_stack.append(None)

        if hasattr(sys, "exc_clear"):
            sys.exc_clear()

        # 将 ctx 放入到 RequestLocal中
        _request_ctx_stack.push(self)

        if self.session is None:
            session_interface = self.app.session_interface
            self.session = session_interface.open_session(self.app, self.request)

            if self.session is None:
                self.session = session_interface.make_null_session(self.app)

        if self.url_adapter is not None:
            self.match_request()
```

![image-20240505001449654](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240505001449654-231d0a.png)

![image-20240505001712503](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240505001712503-06a9f1.png)

2. 创建app_ctx = AppContext对象，其内部封装了App和g。 

![image-20240505000926160](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240505000926160-7b429d.png)

![image-20240505001319779](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240505001319779-5b7b07.png)

- 然后ctx.push触发将 ctx 和 app_ctx 分别通过自己的LocalStack对象将其放入到Local中，Local的本质是以线程ID为key，以{“stack”:[]}为value的字典。

  ```
  {
  	1111:{“stack”:[ctx,]}
  }
  
  {
  	1111:{“stack”:[app_ctx,]}
  }
  ```

  注意：以后再想要获取 request/session / app / g时，都需要去local中获取。 

- 通过url_path从Map中找出Rule规则

![image-20240505002935285](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240505002935285-a76927.png)

![image-20240505002304698](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240505002304698-bd7119.png)

```python
# 下面代码的控制核心
    def full_dispatch_request(self):
        # 尝试触发before_first_request
        self.try_trigger_before_first_request_functions()
        try:
            # 信号(钩子，可以在触发式设置操作)
            request_started.send(self)
            # 执行before_request
            rv = self.preprocess_request()
            if rv is None:
                # 执行视图函数
                rv = self.dispatch_request()
        except Exception as e:
            rv = self.handle_user_exception(e)
        # 将得到的结果序列化返回，得到Response对象
        return self.finalize_request(rv)
```

为什么before_first_request只执行一次？

![image-20240505014813623](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240505014813623-28d79d.png)

- 函数执行流程

![image-20240505013536261](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240505013536261-7f2f67.png)

- 执行所有的before_request函数
  - 这个地方使用chain的原因是：蓝图中不仅有蓝图的before_request要执行，全局的before_request也要执行，所以需要将两个列表进行合二为一，得到一个迭代器对象，方便遍历执行

![image-20240505015757301](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240505015757301-b15010.png)

- 执行视图函数
- 执行所有after_request函数（session加密放到cookie中）

![image-20240505014116043](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240505014116043-b21f68.png)

response的诞生

![image-20240505012616352](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240505012616352-56ce83.png)

销毁ctx和app_ctx

![image-20240505022829927](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240505022829927-8f66e9.png)

和带返回值的wsgi进行类比

![image-20240505023818098](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240505023818098-7384e5.png)

### 8.了解源码流程之后，使用：session、request、app、g

- 偏函数

  ```python
  import functools
  
  # 偏函数
  def func(a1,a2):
      print(a1,a2)
  
  # 使用partial进行绑定参数形成新函数，之后的函数都可以一个参数调用
  # 适合一个参数固定的那种情况
  new_func = functools.partial(func,123)
  new_func(2)
  ```

- 在flask中使用偏函数

  ```python
  def _lookup_req_object(name):
      # ctx
      top = _request_ctx_stack.top
      if top is None:
          raise RuntimeError(_request_ctx_err_msg)
      # ctx.request
      # ctx.session
      return getattr(top, name)
  
  
  new_func1 = functools.partial(_lookup_req_object, "request")
  v = new_func1() # request
  
  new_func2 = functools.partial(_lookup_req_object, "session")
  y = new_func2() # session
  ```

  ![image-20240505105006613](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240505105006613-b37440.png)

  ```python
  # 这个类的本质就是session/request的代理(处理request和session)
  class LocalProxy(object):
      def __init__(self, xxx):
          self.xxx = xxx()  # ctx.session   / ctx.reqeust
  
      def __setitem__(self, key, value):
          self.xxx[key] = value  # ctx.session[key] = value
  
      def __getitem__(self, item):
          return self.xxx[item]  # ctx.session[item]
  
      def __getattr__(self, item):
          return getattr(self.xxx, item)  # ctx.request.method
  
  
  def func():
      return ctx.session
  
  
  x1 = LocalProxy(func)
  # 执行__setitem__
  x1['k1'] = 123
  # 执行__getitem__
  x1['k8']
  
  
  def function():
      return ctx.request
  
  
  x2 = LocalProxy(function)
  # 执行__getattr__方法
  print(x2.method)
  ```

- 私有成员

  ```python
  class Foo:
      def __init__(self):
          self.name = 'alex'
          self.__age = 123
  
  
  obj = Foo()
  
  print(obj.name)
  # 不符合开发规范，但是确实可以用
  print(obj._Foo__age)
  ```

- LocalProxy的源码

  ```python
  import functools
  class LocalProxy(object):
      def __init__(self, local):
          object.__setattr__(self, "_LocalProxy__local", local) # self.__local = local
  
      def _get_current_object(self):
          return self.__local() # self._LocalProxy__local()
  
      def __setitem__(self, key, value):
          # ctx.session[key] = value
          self._get_current_object()[key] = value
  
      def __getattr__(self, name):
          # ctx.request.method
          return getattr(self._get_current_object(), name)
  
  def _lookup_req_object(name):
      top = _request_ctx_stack.top
      if top is None:
          raise RuntimeError(_request_ctx_err_msg)
      return getattr(top, name)
  
  
  session = LocalProxy(functools.partial(_lookup_req_object, "session")) # 函数()  自动传入session
  session['k1'] = 123
  
  
  request = LocalProxy(functools.partial(_lookup_req_object, "request")) # 函数() 自动传入request
  request.method
  ```

  ```python
  # session, request, current_app, g 全部都是LocalProxy对象。
  """
  session['x'] = 123     ctx.session['x'] = 123
  request.method         ctx.request.method
  current_app.config    app_ctx.app.config
  g.x1                  app_ctx.g.x1
  """
  ```

### 9.g到底是个什么鬼？

```
在一次请求请求的周期，可以在g中设置值，在本次的请求周期中都可以读取或复制。
相当于是一次请求周期的全局变量。 
```

```python
from flask import Flask,g

app = Flask(__name__,static_url_path='/xx')

@app.before_request
def f1():
    g.x1 = 123

@app.after_request
def f1(response):
    print(g.x1)
    return response

# 只要before_request之前创建的g对象，然后after_request之后的auto_pop中销毁的，之间的所有过程中都可以使用

@app.route('/index')
def index():
    print(g.x1)
    return 'hello world'


if __name__ == '__main__':
    app.run()
```

## 总结

- 第一阶段：启动flask程序，加载特殊装饰器、路由，把他们封装  app= Flask对象中。 
- 第二阶段：请求到来
  - 创建上下文对象：应用上下文、请求上下文。
  - 执行before / 视图 / after 
  - 销毁上下文对象 

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

