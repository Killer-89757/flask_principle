# flask 源码解析：请求

这是 flask 源码解析系列文章的其中一篇，本系列所有文章列表：

- [flask 源码解析：简介](./flask 源码解析：简介.md)
- [flask 源码解析：应用启动流程](./flask 源码解析：应用启动流程.md)
- [flask 源码解析：路由](./flask 源码解析：路由.md)
- [flask 源码解析：上下文](./flask 源码解析：上下文.md)
- [flask 源码解析：请求](./flask 源码解析：请求.md)
- [flask 源码解析：响应](./flask 源码解析：响应.md)
- [flask 源码解析：session](./flask 源码解析：session.md)

## 简介

对于物理链路来说，请求只是不同电压信号，它根本不知道也不需要知道请求格式和内容到底是怎样的；
对于 TCP 层来说，请求就是传输的数据（二进制的数据流），它只要发送给对应的应用程序就行了；
对于 HTTP 层的服务器来说，请求必须是符合 HTTP 协议的内容；
对于 WSGI server 来说，请求又变成了文件流，它要读取其中的内容，把 HTTP 请求包含的各种信息保存到一个字典中，调用 WSGI app；
对于 flask app 来说，请求就是一个对象，当需要某些信息的时候，只需要读取该对象的属性或者方法就行了。

可以看到，虽然是同样的请求数据，在不同的阶段和不同组件看来，是完全不同的形式。因为每个组件都有它本身的目的和功能，这和生活中的事情一个道理：对于同样的事情，不同的人或者同一个人不同人生阶段的理解是不一样的。

这篇文章呢，我们只考虑最后一个内容，flask 怎么看待请求。

## 请求

我们知道要访问 flask 的请求对象非常简单，只需要 `from flask import request`：

```python
from flask import request

with app.request_context(environ):
    assert request.method == 'POST'
```

前面[一篇文章](https://cizixs.com/2017/01/13/flask-insight-context) 已经介绍了这个神奇的变量是怎么工作的，它最后对应了 `flask.wrappers:Request` 类的对象。
这个类内部的实现虽然我们还不清楚，但是我们知道它接受 WSGI server 传递过来的 `environ` 字典变量，并提供了很多常用的属性和方法可以使用，比如请求的 method、path、args 等。
请求还有一个不那么明显的特性——它不能被应用修改，应用只能读取请求的数据。

这个类的定义很简单，它继承了 `werkzeug.wrappers:Request`，然后添加了一些属性，这些属性和 flask 的逻辑有关，比如 view_args、blueprint、json 处理等。它的代码如下：

```python
from werkzeug.wrappers import Request as RequestBase


class Request(RequestBase):
    """
    The request object is a :class:`~werkzeug.wrappers.Request` subclass and
    provides all of the attributes Werkzeug defines plus a few Flask
    specific ones.
    """

    #: The internal URL rule that matched the request.  This can be
    #: useful to inspect which methods are allowed for the URL from
    #: a before/after handler (``request.url_rule.methods``) etc.
    url_rule = None

    #: A dict of view arguments that matched the request.  If an exception
    #: happened when matching, this will be ``None``.
    view_args = None

    @property
    def max_content_length(self):
        """Read-only view of the ``MAX_CONTENT_LENGTH`` config key."""
        ctx = _request_ctx_stack.top
        if ctx is not None:
            return ctx.app.config['MAX_CONTENT_LENGTH']

    @property
    def endpoint(self):
        """The endpoint that matched the request.  This in combination with
        :attr:`view_args` can be used to reconstruct the same or a
        modified URL.  If an exception happened when matching, this will
        be ``None``.
        """
        if self.url_rule is not None:
            return self.url_rule.endpoint

    @property
    def blueprint(self):
        """The name of the current blueprint"""
        if self.url_rule and '.' in self.url_rule.endpoint:
            return self.url_rule.endpoint.rsplit('.', 1)[0]

    @property
    def is_json(self):
        mt = self.mimetype
        if mt == 'application/json':
            return True
        if mt.startswith('application/') and mt.endswith('+json'):
            return True
        return False
```

这段代码没有什难理解的地方，唯一需要说明的就是 `@property` 装饰符能够把类的方法变成属性，这是 python 中经常见到的用法。

接着我们就要看 `werkzeug.wrappers:Request`：

```python
class Request(BaseRequest, AcceptMixin, ETagRequestMixin,
              UserAgentMixin, AuthorizationMixin,
              CommonRequestDescriptorsMixin):

    """Full featured request object implementing the following mixins:

    - :class:`AcceptMixin` for accept header parsing
    - :class:`ETagRequestMixin` for etag and cache control handling
    - :class:`UserAgentMixin` for user agent introspection
    - :class:`AuthorizationMixin` for http auth handling
    - :class:`CommonRequestDescriptorsMixin` for common headers
    """
```

这个方法有一点比较特殊，它没有任何的 body。但是有多个基类，第一个是 `BaseRequest`，其他的都是各种 `Mixin`。
这里要讲一下 Mixin 机制，这是 python 多继承的一种方式，如果你希望某个类可以自行组合它的特性（比如这里的情况），或者希望某个特性用在多个类中，就可以使用 Mixin。
如果我们只需要能处理各种 `Accept` 头部的请求，可以这样做：

```python
class Request(BaseRequest, AcceptMixin)
    pass
```

但是不要滥用 Mixin，在大多数情况下子类继承了父类，然后实现需要的逻辑就能满足需求。

我们先来看看 `BaseRequest`:

```python
class BaseRequest(object):
    def __init__(self, environ, populate_request=True, shallow=False):
        self.environ = environ
        if populate_request and not shallow:
            self.environ['werkzeug.request'] = self
        self.shallow = shallow
```

能看到实例化需要的唯一变量是 `environ`，它只是简单地把变量保存下来，并没有做进一步的处理。`Request` 的内容很多，其中相当一部分是被 `@cached_property` 装饰的方法，比如下面这种：

```python
    @cached_property
    def args(self):
        """The parsed URL parameters."""
        return url_decode(wsgi_get_bytes(self.environ.get('QUERY_STRING', '')),
                          self.url_charset, errors=self.encoding_errors,
                          cls=self.parameter_storage_class)

    @cached_property
    def stream(self):
        """The stream to read incoming data from.  Unlike :attr:`input_stream`
        this stream is properly guarded that you can't accidentally read past
        the length of the input.  Werkzeug will internally always refer to
        this stream to read data which makes it possible to wrap this
        object with a stream that does filtering.
        """
        _assert_not_shallow(self)
        return get_input_stream(self.environ)

    @cached_property
    def form(self):
        """The form parameters."""
        self._load_form_data()
        return self.form

    @cached_property
    def cookies(self):
        """Read only access to the retrieved cookie values as dictionary."""
        return parse_cookie(self.environ, self.charset,
                            self.encoding_errors,
                            cls=self.dict_storage_class)

    @cached_property
    def headers(self):
        """The headers from the WSGI environ as immutable
        :class:`~werkzeug.datastructures.EnvironHeaders`.
        """
        return EnvironHeaders(self.environ)
```

`@cached_property` 从名字就能看出来，它是 `@property` 的升级版，添加了缓存功能。我们知道
`@property` 能把某个方法转换成属性，每次访问属性的时候，它都会执行底层的方法作为结果返回。
`@cached_property` 也一样，区别是只有第一次访问的时候才会调用底层的方法，后续的方法会直接使用之前返回的值。
那么它是如何实现的呢？我们能在 `werkzeug.utils` 找到它的定义：

```python
class cached_property(property):

    """A decorator that converts a function into a lazy property.  The
    function wrapped is called the first time to retrieve the result
    and then that calculated result is used the next time you access
    the value.

    The class has to have a `__dict__` in order for this property to
    work.
    """

    # implementation detail: A subclass of python's builtin property
    # decorator, we override __get__ to check for a cached value. If one
    # choses to invoke __get__ by hand the property will still work as
    # expected because the lookup logic is replicated in __get__ for
    # manual invocation.

    def __init__(self, func, name=None, doc=None):
        self.__name__ = name or func.__name__
        self.__module__ = func.__module__
        self.__doc__ = doc or func.__doc__
        self.func = func

    def __set__(self, obj, value):
        obj.__dict__[self.__name__] = value

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = obj.__dict__.get(self.__name__, _missing)
        if value is _missing:
            value = self.func(obj)
            obj.__dict__[self.__name__] = value
        return value
```

这个装饰器同时也是实现了 `__set__` 和 `__get__` 方法的[描述器](https://cizixs.com/2015/12/31/python-descriptor-introduction)。
访问它装饰的属性，就会调用 `__get__` 方法，这个方法先在 `obj.__dict__` 中寻找是否已经存在对应的值。如果存在，就直接返回；如果不存在，调用底层的函数
`self.func`，并把得到的值保存起来，再返回。这也是它能实现缓存的原因：因为它会把函数的值作为属性保存到对象中。

关于 `Request` 内部各种属性的实现，就不分析了，因为它们每个具体的实现都不太一样，也不复杂，无外乎对 `environ` 字典中某些字段做一些处理和计算。
接下来回过头来看看 Mixin，这里只用 `AcceptMixin` 作为例子：

```python
class AcceptMixin(object):

    @cached_property
    def accept_mimetypes(self):
        return parse_accept_header(self.environ.get('HTTP_ACCEPT'), MIMEAccept)

    @cached_property
    def accept_charsets(self):
        return parse_accept_header(self.environ.get('HTTP_ACCEPT_CHARSET'),
                                   CharsetAccept)

    @cached_property
    def accept_encodings(self):
        return parse_accept_header(self.environ.get('HTTP_ACCEPT_ENCODING'))

    @cached_property
    def accept_languages(self):
        return parse_accept_header(self.environ.get('HTTP_ACCEPT_LANGUAGE'),
                                   LanguageAccept)
```

`AcceptMixin` 实现了请求内容协商的部分，比如请求接受的语言、编码格式、相应内容等。
它也是定义了很多 `@cached_property` 方法，虽然自己没有 `__init__` 方法，但是也直接使用了
`self.environ`，因此它并不能直接使用，只能和 `BaseRequest` 一起出现。

## 参考资料

- [Flask official docs](http://flask.pocoo.org/docs/0.12/)