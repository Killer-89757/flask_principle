# Flask教程(十九)SocketIO

### 软硬件环境

- windows 10 64bit
- anaconda3 with [python](https://xugaoxiang.com/tag/python/) 3.7
- pycharm 2020.1.2
- [flask](https://xugaoxiang.com/tag/flask/) 1.1.2
- [flask](https://xugaoxiang.com/tag/flask/)-[socketio](https://xugaoxiang.com/tag/socketio/) 4.3.1

### 什么是websocket

`WebSocket`是一种网络通讯协议，与`HTTP`不同的是，**`WebSocket`提供全双工通信**。也就是说，传统的方式，只有当客户端发起请求后，服务器端才会发送数据，**而`WebSocket`可以让服务器主动发送数据给客户端，它是服务器推送技术的一种**。

下图是`WebSocket`和`HTTP`的区别

![websocket](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F5cd4dc6d8650a6b9-ff477f.png)

### websocketd

下载地址：http://websocketd.com/#download

`websocketd`是一款非常不错的`WebSocket`服务器，我们首先利用它来了解下标准`WebSocket`的交互方式。先来下载`windows`版本的`websocketd`，解压之后进入目录

下面开始编写测试脚本，使用`python`语言，文件名是`test.py`，脚本的作用是周期性的向标准输出`stdout`打印一个数值

```
from sys import stdout
from time import sleep

for count in range(0, 10):
  print(count + 1)
  stdout.flush()
  sleep(0.5)
```

开启服务

```
websocketd --port 8080 python test.py
```

现在需要一个`WebSocket`客户端，我们来到`chrome`商店，安装插件 https://chrome.google.com/webstore/detail/websocket-test-client/fgponpodhbmadfljofbimhhlengambbn , 然后打开插件，输入`WebSocket`的`url`就可以看到服务器端的输出了

![websocketd](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fe5e78abb7aa65287-b0f9c2.png)

![websocketd](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F14bf1551ca6e3cfe-ac7fd0.png)

![websocketd](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F4b78e182054a84fa-37fdaa.png)

### [flask](https://xugaoxiang.com/tag/flask/)-[socketio](https://xugaoxiang.com/tag/socketio/)

`Flask-SocketIO`使`Flask`应用程序能够访问客户端和服务器之间的低延迟双向通信。客户端应用程序可以使用`Javascript`，`C++`，`Java`和`Swift`中的任何`SocketIO`官方客户端库或任何兼容的客户端来建立与服务器的永久连接。

### 异步模式

```
flask-socketio`需要底层异步服务的支持，比较灵活的是，它会自己检测当前环境中存在的异步服务，且使用顺序为 `eventlet` --> `gevent` --> `werkzeug
```

- `eventlet` 性能最佳，支持长轮询和`WebSocket`传输
- `gevent` 在许多不同的配置中得到支持。`gevent`完全支持长轮询传输，但与`eventlet`不同，`gevent`没有本机`WebSocket`支持。要添加对`WebSocket`的支持，目前有两种选择：安装`gevent-websocket`包为`gevent`增加`WebSocket`支持，或者可以使用带有`WebSocket`功能的`uWSGI Web`服务器。`gevent`的使用也是一种高性能选项，但略低于`eventlet`
- `werkzeug` 也可以使用基于`werkzeug`的`Flask`开发服务器，但需要注意的是，它缺乏其他两个选项的性能，因此只应用于简单的开发环境，而且它也仅支持长轮询传输

### 安装

直接使用`pip`来安装

```python
pip install eventlet
pip install flask-socketio
```

### 示例代码

先看服务端代码

文件`run.py`

```python
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'

socketio = SocketIO()
socketio.init_app(app, cors_allowed_origins='*')

name_space = '/dcenter'


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/push')
def push_once():
    event_name = 'dcenter'
    broadcasted_data = {'data': "test message!"}
    socketio.emit(event_name, broadcasted_data, broadcast=False, namespace=name_space)
    return 'done!'

@socketio.on('connect', namespace=name_space)
def connected_msg():
    print('client connected.')


@socketio.on('disconnect', namespace=name_space)
def disconnect_msg():
    print('client disconnected.')


@socketio.on('my_event', namespace=name_space)
def mtest_message(message):
    print(message)
    emit('my_response',
         {'data': message['data'], 'count': 1})


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
```

代码中，我们设定了命名空间`namespace`，因为客户端在进行连接的时候需要用到的`url`就包含`namespace`，另外还有个概念，就是`event`，`connect`、`disconnect`还有自定义的`my_event`都是

文件`index.html`的代码如下

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SocketIO Demo</title>
    <script type="text/javascript" src="//cdn.bootcss.com/jquery/3.1.1/jquery.min.js"></script>
    <script type="text/javascript" src="//cdn.bootcss.com/socket.io/3.0.0/socket.io.min.js"></script>
</head>
<body>

<h2>Demo of SocketIO</h2>
<div id="t"></div>
<script>
$(document).ready(function () {
    namespace = '/dcenter';
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);
    socket.on('dcenter', function (res) {
        var t = res.data;
        if (t) {
            $("#t").append(t).append('<br/>');
        }
    });
});
</script>
</body>
</html>
```

启动服务后，我们访问 [http://127.0.0.1:5000](http://127.0.0.1:5000/)， 并保持这个页面不动，因为，后面接收到的消息会显示在这个页面上

![flask-socketio](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Ff97dc29ebe9b66b1-5cd219.png)

这时候，使用浏览器访问 http://127.0.0.1:5000/push

![flask-socketio](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F85801b6ce42c1ed5-2bc9f3.png)

我们使用这种方式来触发服务器发送消息给客户端，再次回到之前的页面，可以看到已经把服务器端发送过来的消息显示在了页面上

![flask-socketio](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fb281eaed3eda451e-0ab0d9.png)

注意到，上面`javascript`中，`url`中使用的协议是`http`，而不是`ws`，这一点跟原生的`WebSocket`有点区别。

### cors跨域错误

如果是前后端分离的系统中，会出现如下的错误

```python
Traceback (most recent call last):
  File "src\\gevent\\greenlet.py", line 854, in gevent._gevent_cgreenlet.Greenlet.run
  File "C:\ProgramData\Anaconda3\envs\FlaskTutorial\lib\site-packages\gevent\baseserver.py", line 34, in _handle_and_close_when_done
    return handle(*args_tuple)
  File "C:\ProgramData\Anaconda3\envs\FlaskTutorial\lib\site-packages\gevent\server.py", line 233, in wrap_socket_and_handle
    with _closing_socket(self.wrap_socket(client_socket, **self.ssl_args)) as ssl_socket:
TypeError: wrap_socket() got an unexpected keyword argument 'cors_allowed_origins'
2020-09-09T08:16:07Z <Greenlet at 0x1812f1e8bf8: _handle_and_close_when_done(<bound method StreamServer.wrap_socket_and_handle , <bound method StreamServer.do_close
of <WSGIServer, (<gevent._socket3.socket [closed] at 0x1812fc41cc8)> failed with TypeError
```

这是跨域的问题，经测试发现，使用之前介绍过的`flask-cors`来处理，其实并不起作用，我们需要在`socketio`初始化的时候加入必要的参数

```
socketio = SocketIO()
socketio.init_app(app, cors_allowed_origins='*')
```

详细的信息可以参考这个链接， https://github.com/eventlet/eventlet/issues/526