# Flask教程(五)GET和POST

- Windows 10 64bit
- Anaconda3 with [python](https://xugaoxiang.com/tag/python/) 3.7
- PyCharm 2019.3
- Flask 1.1.1

### HTTP简介

`HTTP`是`HyperText Transfer Protocol`的缩写，它是互联网数据传输的基础。在`Flask`框架中，同样提供了进行数据交互的`HTTP`方法。

### HTTP方法

常用的`HTTP`请求方法如下表所示

| HTTP方法 |                             描述                             |
| :------: | :----------------------------------------------------------: |
|   GET    |             请求指定的资源，被认为是不安全的方法             |
|   POST   | 会向服务器提交数据，请求服务器进行处理，如表单提交、文件上传 |
|   HEAD   | 与GET方法一样，但是服务器不会回传响应主体，常用来查看服务器的性能 |
|   PUT    |                       向服务器上传内容                       |
|  DELETE  |                   请求服务器删除所请求URI                    |

### Flask处理GET和POST

在实际场景中，应用最多的就是`GET`和`POST`方法了。在`Flask`中，我们可以在`Flask`对象的`route`方法中指定`HTTP`方法，如果不写的话，默认的就是`GET`。为了在服务器端处理`POST`请求，让我们先创建一个表单来获取用户的输入。来看实例

`index.html`文件内容

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>GET and POST</title>
</head>
<body>
    <form action = "http://localhost:5000" method = "post">
         <table>
            <tr>
                <td>Name</td>
                <td><input type ="text" name ="username"></td>
            </tr>
            <tr>
                <td>Password</td>
                <td><input type ="password" name ="password"></td>
            </tr>
            <tr>
                <td><input type = "submit"></td>
            </tr>
        </table>
    </form>
</body>
</html>
```

这里我们在`form`中指定的是`POST`方法。接下来在`run.py`文件中处理请求

```python
from flask import Flask, request
app = Flask(__name__)

@app.route('/', methods=['POST'])
def index():
    username = request.form['username']
    password = request.form['password']
    if username == "waws" and password == "123456":
        return f"<html><body>Welcome {username}</body></html>"
    else:
        return f"<html><body>Welcome!</body></html>"

if __name__ == '__main__':
    app.run(debug=True)
```

可以看到，在`@app.route`中，我们也指定了`POST`方法，然后通过`flask`中的`request`对象来获取`form`表单的数据，接着进行一个简单判断，返回不同的网页内容。

我们用浏览器打开`index.html`，在用户名和密码框中输入waws和123456，点击提交，就会跳转到显示`Welcome waws`的页面，否则跳转到显示`Welcome`的页面，如下图

![flask](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F2a329d3b2e921118-53d0a4.png)

![flask](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F2a329d3b2e921118-42ec1b.png)

![flask](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F34c25f7d25d19ea1-3a5274.png)

接下来看看客户端采用`GET`请求的实例，我们在上面的基础上进行修改即可。

```html
index.html`文件，将原来的`post`改为`get
<form action = "http://localhost:5000" method = "get">
    <table>
            <tr>
                <td>Name</td>
                <td><input type ="text" name ="username"></td>
            </tr>
            <tr>
                <td>Password</td>
                <td><input type ="password" name ="password"></td>
            </tr>
            <tr>
                <td><input type = "submit"></td>
            </tr>
    </table>
</form>
```

`run.py`中将原来的`POST`改为`GET`，表单的接收也适当修改下

```python
@app.route('/', methods=['GET'])
def index():
    username = request.args.get('username')
    password = request.args.get('password')
    if username == "waws" and password == "123456":
        return f"<html><body>Welcome {username}</body></html>"
    else:
        return f"<html><body>Welcome!</body></html>"
```

整个运行的结果是一模一样的，但是注意到表单提交之后的地址栏信息，如下

![flask](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2FSnipaste_2021-02-16_21-55-01-037983.png)

后面多出了`?username=waws&password=123456`，`GET`请求会将表单的数据以键值对的形式拼接到`URL`后发送给服务器。这就是`GET`和`POST`最重要的区别，对于一些敏感信息，`GET`方法是及其不安全的，千万不要这样使用。

