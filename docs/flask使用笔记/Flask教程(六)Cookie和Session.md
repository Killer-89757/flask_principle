# Flask教程(六)Cookie和Session

### 软硬件环境

- Windows 10 64bit
- Anaconda3 with [python](https://xugaoxiang.com/tag/python/) 3.7
- PyCharm 2019.3
- Flask 1.1.1

### 什么是Cookie

`Cookie`是客户端保存用户信息的一种机制，用来记录用户的一些信息，实际上`Cookie`是服务器在本地机器上存储的一小段文本，并随着每次请求发送到服务器。客户端和服务器的交互图如下

![flask](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F6e0016b7ca199aa4-a7ec77.png)

![flask](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F93e59196dfe3674e-d1fa12.png)

### Cookie实例

在`Flask`中，通过`flask`对象的`make_response`来构建响应体，然后通过`set_cookie`来设置`cookie`，它是一个键值对数据。下面是一个`Cookie`的简单实例

`run.py`文件内容

```python
from flask import Flask, make_response
app = Flask(__name__)

@app.route('/cookie', methods=['GET'])
def cookie():
    resp = make_response("<html><body>Cookie</body></html>")
    resp.set_cookie('name', 'waws')
    return resp

if __name__ == '__main__':
    app.run(host="127.0.0.1",port=5000,debug=True)
```

启动`Flask`服务后，访问http://127.0.0.1:5000/cookie

![flask](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fe88ff4b13f26e07f-516ff2.png)

这里推荐个`chrome`浏览器的[Cookie插件](https://chrome.google.com/webstore/detail/cookies/iphcomljdfghbkdcfndaijbokpgddeno/related)，它可以很方便的查看、修改、删除`Cookie`信息。

在这个例子中，我们看到保存在本地的`Flask`服务端设置的`Cookie`信息，('name'：'waws')

![flask](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F8d69976deed03c0e-7acddb.png)

### 什么是Session

`Session`跟上面的`Cookie`非常类似，只不过`Session`是存储在服务器端的，在实际场景中经常遇到的登录失效，就是因为`Session`在起作用。

### Session实例

在`Flask`中，使用`session`对象来存放键值对。需要注意的是，**使用`Session`需要设置`app.secret_key`**。来看下面的实例

`run.py`文件内容

```python
from flask import Flask, render_template, make_response, session
app = Flask(__name__)
app.secret_key = "test"

@app.route('/session', methods=['GET'])
def sess():
    resp = make_response("<html><body>Session.<a href='/getValue'>Get Value</a></body></html>")
    session['name'] = 'waws'
    return resp

@app.route('/getValue')
def getValue():
    if 'name' in session:
        name = session['name']
        return render_template('getvalue.html', name=name)

if __name__ == '__main__':
    app.run(host="127.0.0.1",port=5000,debug=True)
```

来到模板文件，`getvalue.html`文件内容

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>GetValue</title>
</head>
<body>
<p>Session value: <b> {{ name }} </b> </p>
</body>
</html>
```

启动`Flask`服务，访问http://127.0.0.1:5000/session

![flask](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F605d3b8f69e89b31-3c5700.png)

点击超链接，进入`getvalue.html`页面

![image-20240505220824653](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240505220824653-3b6658.png)