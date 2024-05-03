# flask 源码解析：应用启动流程

这是 flask 源码解析系列文章的其中一篇，本系列所有文章列表：

- [flask 源码解析：简介](./flask 源码解析：简介.md)
- [flask 源码解析：应用启动流程](./flask 源码解析：应用启动流程.md)
- [flask 源码解析：路由](./flask 源码解析：路由.md)
- [flask 源码解析：上下文](./flask 源码解析：上下文.md)
- [flask 源码解析：请求](./flask 源码解析：请求.md)
- [flask 源码解析：响应](./flask 源码解析：响应.md)
- [flask 源码解析：session](./flask 源码解析：session.md)

## WSGI

所有的 python web 框架都要遵循 WSGI 协议，如果对 WSGI 不清楚，可以查看我[之前的介绍文章](https://cizixs.com/2014/11/08/understand-wsgi)。

在这里还是要简单回顾一下 WSGI 的核心概念。

WSGI 中有一个非常重要的概念：每个 python web 应用都是一个可调用（callable）的对象。在 flask 中，这个对象就是 `app = Flask(__name__)` 创建出来的 `app`，就是下图中的绿色 Application 部分。要运行 web 应用，必须有 web server，比如我们熟悉的 apache、nginx ，或者 python 中的 [gunicorn](http://gunicorn.org/) ，我们下面要讲到的 `werkzeug` 提供的 `WSGIServer`，它们是下图的黄色 Server 部分。

Server 和 Application 之间怎么通信，就是 WSGI 的功能。它规定了 `app(environ, start_response)` 的接口，server 会调用 application，并传给它两个参数：`environ` 包含了请求的所有信息，`start_response` 是 application 处理完之后需要调用的函数，参数是状态码、响应头部还有错误信息。

WSGI application 非常重要的特点是：**它是可以嵌套的。**换句话说，我可以写个 application，它做的事情就是调用另外一个 application，然后再返回（类似一个 proxy）。一般来说，嵌套的最后一层是业务应用，中间就是 middleware。这样的好处是，可以解耦业务逻辑和其他功能，比如限流、认证、序列化等都实现成不同的中间层，不同的中间层和业务逻辑是不相关的，可以独立维护；而且用户也可以动态地组合不同的中间层来满足不同的需求。

WSGI 的内容就讲这么多，我们来看看 flask 的 hello world 应用：

```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run()
```

这里的 `app = Flask(__name__)` 就是上面提到的 Application 部分，但是我们并没有看到 Server 的部分，那么它一定是隐藏到 `app.run()` 内部某个地方了。

## 启动流程

应用启动的代码是 `app.run()` ，这个方法的代码如下：

```python
def run(self, host=None, port=None, debug=None, **options):
    """Runs the application on a local development server."""
    from werkzeug.serving import run_simple

    # 如果host 和 port 没有指定，设置 host 和 port 的默认值 127.0.0.1 和 5000
    if host is None:
        host = '127.0.0.1'
    if port is None:
        server_name = self.config['SERVER_NAME']
        if server_name and ':' in server_name:
            port = int(server_name.rsplit(':', 1)[1])
        else:
            port = 5000

    # 调用 werkzeug.serving 模块的 run_simple 函数，传入收到的参数
    # 注意第三个参数传进去的是 self，也就是要执行的 web application
    try:
        run_simple(host, port, self, **options)
    finally:
        self._got_first_request = False
```

**NOTE**：为了阅读方便，我删除了注释和不相干的部分，下面所有的代码都会做类似的处理，不再赘述。

这个方法的内容非常简单：处理一下参数，然后调用 `werkzeug` 的 `run_simple`。需要注意的是：`run_simple` 的第三个参数是 `self`，也就是我们创建的 `Flask()` application。因为 WSGI server 不是文章的重点，所以我们就不深入讲解了。现在只需要知道它的功能就行：监听在指定的端口，收到 HTTP 请求的时候解析为 WSGI 格式，然后调用 `app` 去执行处理的逻辑。对应的执行逻辑在 `werkzeug.serving:WSGIRequestHandler` 的 `run_wsgi` 中有这么一段代码：

```python
def execute(app):
    application_iter = app(environ, start_response)
    try:
        for data in application_iter:
            write(data)
        if not headers_sent:
            write(b'')
    finally:
        if hasattr(application_iter, 'close'):
            application_iter.close()
            application_iter = None
```

可以看到 `application_iter = app(environ, start_response)` 就是调用代码获取结果的地方。

要调用 `app` 实例，那么它就需要定义了 `__call__` 方法，我们找到 `flask.app：Flask` 对应的内容：

```python
def __call__(self, environ, start_response):
    """Shortcut for :attr:`wsgi_app`."""
    return self.wsgi_app(environ, start_response)

def wsgi_app(self, environ, start_response):
    """The actual WSGI application.
    """
    # 创建请求上下文，并把它压栈。这个在后面会详细解释
    ctx = self.request_context(environ)
    ctx.push()
    error = None

    try:
        try:
            # 正确的请求处理路径，会通过路由找到对应的处理函数
            response = self.full_dispatch_request()
        except Exception as e:
            # 错误处理，默认是 InternalServerError 错误处理函数，客户端会看到服务器 500 异常
            error = e
            response = self.handle_exception(e)
        return response(environ, start_response)
    finally:
        if self.should_ignore_error(error):
            error = None
        # 不管处理是否发生异常，都需要把栈中的请求 pop 出来
        ctx.auto_pop(error)
```

上面这段代码只有一个目的：找到处理函数，然后调用它。除了异常处理之外，我们还看到了 `context` 相关的内容（开始有 `ctx.push()`，最后有 `ctx.auto_pop()`的逻辑），它并不影响我们的理解，现在可以先不用管，后面会有一篇文章专门介绍。

继续往后看，`full_dsipatch_request` 的代码如下：

```python
def full_dispatch_request(self):
    """Dispatches the request and on top of that performs request
    pre and postprocessing as well as HTTP exception catching and
    error handling.
    """
    self.try_trigger_before_first_request_functions()
    try:
        request_started.send(self)
        rv = self.preprocess_request()
        if rv is None:
            rv = self.dispatch_request()
    except Exception as e:
        rv = self.handle_user_exception(e)
    return self.finalize_request(rv)
```

这段代码最核心的内容是 `dispatch_request`，加上[请求的 hooks 处理](http://flask.pocoo.org/docs/0.12/reqcontext/#callbacks-and-errors)和错误处理的内容。

NOTE：`self.dispatch_request()` 返回的是处理函数的返回结果（比如 hello world 例子中返回的字符串），`finalize_request` 会把它转换成 `Response` 对象。

在 `dispatch_request` 之前我们看到 `preprocess_request`，之后看到 `finalize_request`，它们里面包括了请求处理之前和处理之后的很多 hooks 。这些 hooks 包括：

- 第一次请求处理之前的 hook 函数，通过 `before_first_request` 定义
- 每个请求处理之前的 hook 函数，通过 `before_request` 定义
- 每个请求正常处理之后的 hook 函数，通过 `after_request` 定义
- 不管请求是否异常都要执行的 `teardown_request` hook 函数

`dispatch_request` 要做的就是找到我们的处理函数，并返回调用的结果，也就是**路由的过程**。我们下一篇文章来讲！