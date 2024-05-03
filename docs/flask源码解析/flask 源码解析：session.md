# flask 源码解析：session

这是 flask 源码解析系列文章的其中一篇，本系列所有文章列表：

- [flask 源码解析：简介](./flask 源码解析：简介.md)
- [flask 源码解析：应用启动流程](./flask 源码解析：应用启动流程.md)
- [flask 源码解析：路由](./flask 源码解析：路由.md)
- [flask 源码解析：上下文](./flask 源码解析：上下文.md)
- [flask 源码解析：请求](./flask 源码解析：请求.md)
- [flask 源码解析：响应](./flask 源码解析：响应.md)
- [flask 源码解析：session](./flask 源码解析：session.md)

## session 简介

在解析 session 的实现之前，我们先介绍一下 session 怎么使用。session 可以看做是在不同的请求之间保存数据的方法，因为 HTTP 是无状态的协议，但是在业务应用上我们希望知道不同请求是否是同一个人发起的。比如购物网站在用户点击进入购物车的时候，服务器需要知道是哪个用户执行了这个操作。

在 flask 中使用 session 也很简单，只要使用 `from flask import session` 导入这个变量，在代码中就能直接通过读写它和 session 交互。

```bash
from flask import Flask, session, escape, request

app = Flask(__name__)
app.secret_key = 'please-generate-a-random-secret_key'


@app.route("/")
def index():
    if 'username' in session:
        return 'hello, {}\n'.format(escape(session['username']))
    return 'hello, stranger\n'


@app.route("/login", methods=['POST'])
def login():
    session['username'] = request.form['username']
    return 'login success'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

上面这段代码模拟了一个非常简单的登陆逻辑，用户访问 `POST /login` 来登陆，后面访问页面的时候 `GET /`，会返回该用户的名字。我们看一下具体的操作实例（下面的操作都是用 [httpie](https://github.com/jkbrzt/httpie) 来执行的，使用 `curl` 命令也能达到相同的效果）：

直接访问的话，我们可以看到返回 `hello stranger`：

```bash
➜  ~ http -v http://127.0.0.1:5000/
GET / HTTP/1.1
Accept: */*
Accept-Encoding: gzip, deflate
Host: 127.0.0.1:5000
User-Agent: HTTPie/0.8.0


HTTP/1.0 200 OK
Content-Length: 14
Content-Type: text/html; charset=utf-8
Date: Wed, 01 Mar 2017 04:22:18 GMT
Server: Werkzeug/0.11.2 Python/2.7.10

hello stranger
```

然后我们模拟登陆请求，`-v` 是打印出请求，`-f` 是告诉服务器这是表单数据，`--session=mysession` 是把请求的 cookie 等信息保存到这个变量中，后面可以通过变量来指定 session：

```bash
➜  ~ http -v -f --session=mysession POST http://127.0.0.1:5000/login username=cizixs
POST /login HTTP/1.1
Accept: */*
Accept-Encoding: gzip, deflate
Content-Length: 15
Content-Type: application/x-www-form-urlencoded; charset=utf-8
Host: 127.0.0.1:5000
User-Agent: HTTPie/0.8.0

username=cizixs

HTTP/1.0 200 OK
Content-Length: 13
Content-Type: text/html; charset=utf-8
Date: Wed, 01 Mar 2017 04:20:54 GMT
Server: Werkzeug/0.11.2 Python/2.7.10
Set-Cookie: session=eyJ1c2VybmFtZSI6ImNpeml4cyJ9.C5fdpg.fqm3FTv0kYE2TuOyGF1mx2RuYQ4; HttpOnly; Path=/

login success
```

最重要的是我们看到 response 中有 `Set-Cookie` 的头部，cookie 的键是 `session`，值是一堆看起来随机的字符串。

继续，这个时候我们用 `--session=mysession` 参数把这次的请求带上保存在 `mysession` 中的信息，登陆后访问，可以看到登陆的用户名：

```bash
➜  ~ http -v --session=mysession http://127.0.0.1:5000/
GET / HTTP/1.1
Accept: */*
Accept-Encoding: gzip, deflate
Cookie: session=eyJ1c2VybmFtZSI6ImNpeml4cyJ9.C5fevg.LE03yEZDWTUMQW-nNkTr1zBEhKk
Host: 127.0.0.1:5000
User-Agent: HTTPie/0.8.0


HTTP/1.0 200 OK
Content-Length: 11
Content-Type: text/html; charset=utf-8
Date: Wed, 01 Mar 2017 04:25:46 GMT
Server: Werkzeug/0.11.2 Python/2.7.10
Set-Cookie: session=eyJ1c2VybmFtZSI6ImNpeml4cyJ9.C5feyg.sfFCDIqfef4i8cvxUClUUGQNcHA; HttpOnly; Path=/

hellocizixs
```

这次注意在发送的请求中，客户端带了 `Cookie` 头部，上面的值保存了前一个请求的 response 给我们设置的值。

总结一下：session 是通过在客户端设置 cookie 实现的，每次客户端发送请求的时候会附带着所有的 cookie，而里面保存着一些重要的信息（比如这里的用户信息），这样服务器端就能知道客户端的信息，然后根据这些数据做出对应的判断，就好像不同请求之间是有记忆的。

## 解析

我们知道 session 是怎么回事了，这部分就分析一下 flask 是怎么实现它的。

### 请求过程

不难想象，session 的大致解析过程是这样的：

- 请求过来的时候，flask 会根据 cookie 信息创建出 session 变量（如果 cookie 不存在，这个变量有可能为空），保存在该请求的上下文中
- 视图函数可以获取 session 中的信息，实现自己的逻辑处理
- flask 会在发送 response 的时候，根据 session 的值，把它写回到 cookie 中

注意：session 和 cookie 的转化过程中，应该考虑到安全性，不然直接使用伪造的 cookie 会是个很大的安全隐患。

在[ flask 上下文那篇文章](https://cizixs.com/2017/01/13/flask-insight-context)中，我们知道，每次请求过来的时候，我们访问的 `request` 和 `session` 变量都是 `RequestContext` 实例的变量。在 `RequestContext.Push()` 方法的最后有这么一段代码：

```python
self.session = self.app.open_session(self.request)
if self.session is None:
    self.session = self.app.make_null_session()
```

它初始化了 `session` 变量，保存在 `RequestContext` 上，这样后面就能直接通过 `from flask import session` 来使用它。如果没有设置 `secret_key` 变量， `open_session` 就会返回 None，这个时候会调用 `make_null_session` 来生成一个空的 session，这个特殊的 session 不能进行任何读写操作，不然会报异常给用户。

我们来看看 `open_session` 方法：

```python
def open_session(self, request):
    return self.session_interface.open_session(self, request)
```

在 `Flask` 中，所有和 session 有关的调用，都是转发到 `self.session_interface` 的方法调用上（这样用户就能用自定义的 `session_interface` 来控制 session 的使用）。而默认的 `session_inerface` 有默认值：

```python
session_interface = SecureCookieSessionInterface()
```

后面遇到 session 有关方法解释，我们会直接讲解 `SecureCookieSessionInterface` 的代码实现，跳过中间的这个转发说明。

```python
null_session_class = NullSession

def make_null_session(self, app):
    return self.null_session_class()

def open_session(self, app, request):
    # 获取 session 签名的算法
    s = self.get_signing_serializer(app)
    if s is None:
        return None

    # 从 cookie 中获取 session 变量的值
    val = request.cookies.get(app.session_cookie_name)
    if not val:
        return self.session_class()

    # 因为 cookie 的数据需要验证是否有篡改，所以需要签名算法来读取里面的值
    max_age = total_seconds(app.permanent_session_lifetime)
    try:
        data = s.loads(val, max_age=max_age)
        return self.session_class(data)
    except BadSignature:
        return self.session_class()
```

`open_session` 根据请求中的 cookie 来获取对应的 session 对象。之所以有 `app` 参数，是因为根据 app 中的安全设置（比如签名算法、secret_key）对 cookie 进行验证。

这里有两点需要特殊说明的：签名算法是怎么工作的？session 对象到底是怎么定义的？

### session 对象

默认的 session 对象是 `SecureCookieSession`，这个类就是一个基本的字典，外加一些特殊的属性，比如 `permanent`（flask 插件会用到这个变量）、`modified`（表明实例是否被更新过，如果更新过就要重新计算并设置 cookie，因为计算过程比较贵，所以如果对象没有被修改，就直接跳过）。

```python
class SessionMixin(object):
    def _get_permanent(self):
        return self.get('_permanent', False)

    def _set_permanent(self, value):
        self['_permanent'] = bool(value)

    #: this reflects the ``'_permanent'`` key in the dict.
    permanent = property(_get_permanent, _set_permanent)
    del _get_permanent, _set_permanent

    modified = True

class SecureCookieSession(CallbackDict, SessionMixin):
    """Base class for sessions based on signed cookies."""

    def __init__(self, initial=None):
        def on_update(self):
            self.modified = True
        CallbackDict.__init__(self, initial, on_update)
        self.modified = False
```

怎么知道实例的数据被更新过呢？ `SecureCookieSession` 是基于 `werkzeug/datastructures:CallbackDict` 实现的，这个类可以指定一个函数作为 `on_update` 参数，每次有字典操作的时候（`__setitem__`、`__delitem__`、`clear`、`popitem`、`update`、`pop`、`setdefault`）会调用这个函数。

**NOTE**：`CallbackDict` 的实现很巧妙，但是并不复杂，感兴趣的可以自己参考代码。主要思路就是重载字典的一些更新操作，让它们在做原来事情的同时，额外调用一下实现保存的某个函数。

对于开发者来说，可以把 `session` 简单地看成字典，所有的操作都是和字典一致的。

### 签名算法

都获取 cookie 数据的过程中，最核心的几句话是：

```python
s = self.get_signing_serializer(app)
val = request.cookies.get(app.session_cookie_name)
data = s.loads(val, max_age=max_age)

return self.session_class(data)
```

其中两句都和 `s` 有关，`signing_serializer` 保证了 cookie 和 session 的转换过程中的安全问题。如果 flask 发现请求的 cookie 被篡改了，它会直接放弃使用。

我们继续看 `get_signing_serializer` 方法：

```python
def get_signing_serializer(self, app):
    if not app.secret_key:
        return None
    signer_kwargs = dict(
        key_derivation=self.key_derivation,
        digest_method=self.digest_method
    )
    return URLSafeTimedSerializer(app.secret_key,
        salt=self.salt,
        serializer=self.serializer,
        signer_kwargs=signer_kwargs)
```

我们看到这里需要用到很多参数：

- `secret_key`：密钥。这个是必须的，如果没有配置 `secret_key` 就直接使用 `session` 会报错
- `salt`：为了增强安全性而设置一个 salt 字符串（可以自行搜索“安全加盐”了解对应的原理）
- `serializer`：序列算法
- `signer_kwargs`：其他参数，包括摘要/hash算法（默认是 `sha1`）和 签名算法（默认是 `hmac`）

`URLSafeTimedSerializer` 是 [`itsdangerous`](https://pythonhosted.org/itsdangerous/) 库的类，主要用来进行数据验证，增加网络中数据的安全性。`itsdangerours` 提供了多种 `Serializer`，可以方便地进行类似 json 处理的数据序列化和反序列的操作。至于具体的实现，因为篇幅限制，就不解释了。

### 应答过程

flask 会在请求过来的时候自动解析 cookie 的值，把它变成 `session` 变量。开发在视图函数中可以使用它的值，也可以对它进行更新。最后再返回的 response 中，flask 也会自动把 session 写回到 cookie。我们来看看这部分是怎么实现的！

[之前的文章](https://cizixs.com/2017/01/22/flask-insight-response)讲解了应答的过程，其中 `finalize_response` 方法在根据视图函数的返回生成 response 对象之后，会调用 `process_response` 方法进行处理。`process_response` 方法的最后有这样两句话：

```python
def process_response(self, response):
    ...
    if not self.session_interface.is_null_session(ctx.session):
        self.save_session(ctx.session, response)
    return response
```

这里就是 session 在应答中出现的地方，思路也很简单，如果需要就调用 `save_sessoin`，把当前上下文中的 `session` 对象保存到 response 。

`save_session` 的代码和 `open_session` 对应：

```python
def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)

        # 如果 session 变成了空字典，flask 会直接删除对应的 cookie
        if not session:
            if session.modified:
                response.delete_cookie(app.session_cookie_name,
                                       domain=domain, path=path)
            return

        # 是否需要设置 cookie。如果 session 发生了变化，就一定要更新 cookie，否则用户可以 `SESSION_REFRESH_EACH_REQUEST` 变量控制是否要设置 cookie
        if not self.should_set_cookie(app, session):
            return

        httponly = self.get_cookie_httponly(app)
        secure = self.get_cookie_secure(app)
        expires = self.get_expiration_time(app, session)
        val = self.get_signing_serializer(app).dumps(dict(session))
        response.set_cookie(app.session_cookie_name, val,
                            expires=expires,
                            httponly=httponly,
                            domain=domain, path=path, secure=secure)
```

这段代码也很容易理解，就是从 `app` 和 `session` 变量中获取所有需要的信息，然后调用 `response.set_cookie` 设置最后的 `cookie`。这样客户端就能在 cookie 中保存 session 有关的信息，以后访问的时候再次发送给服务器端，以此来实现有状态的交互。

## 解密 session

有时候在开发或者调试的过程中，需要了解 cookie 中保存的到底是什么值，可以通过手动解析它的值。`session` 在 `cookie` 中的值，是一个字符串，由句号分割成三个部分。第一部分是 `base64` 加密的数据，第二部分是时间戳，第三部分是校验信息。

前面两部分的内容可以通过下面的方式获取，代码也可直观，就不给出解释了：

```bash
In [1]: from itsdangerous import *

In [2]: s = 'eyJ1c2VybmFtZSI6ImNpeml4cyJ9.C5fdpg.fqm3FTv0kYE2TuOyGF1mx2RuYQ4'

In [3]: data, timstamp, secret = s.split('.')

In [4]: base64_decode(data)
Out[4]: '{"username":"cizixs"}'

In [5]: bytes_to_int(base64_decode(timstamp))
Out[5]: 194502054

In [7]: time.strftime('%Y-%m-%d %H:%I%S', time.localtime(194502054+EPOCH))
Out[7]: '2017-03-01 12:1254'
```

## 总结

flask 默认提供的 session 功能还是很简单的，满足了基本的功能。但是我们看到 flask 把 session 的数据都保存在客户端的 cookie 中，这里只有用户名还好，如果有一些私密的数据（比如密码，账户余额等等），就会造成严重的安全问题。可以考虑使用 [flask-session](https://pythonhosted.org/Flask-Session/) 这个三方的库，它把数据保存在服务器端（本地文件、redis、memcached），客户端只拿到一个 sessionid。

session 主要是用来在不同的请求之间保存信息，最常见的应用就是登陆功能。虽然直接通过 `session` 自己也可以写出来不错的登陆功能，但是在实际的项目中可以考虑 [`flask-login`](https://flask-login.readthedocs.io/en/latest/) 这个三方的插件，方便我们的开发

## 参考资料

- [flask-session github page](https://github.com/fengsp/flask-session)
- [Flask 源码阅读笔记](http://blog.csdn.net/yueguanghaidao/article/details/40016235)