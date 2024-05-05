# Flask教程(八)重定向

### 软硬件环境

- Windows 10 64bit
- Anaconda3 with [python](https://xugaoxiang.com/tag/python/) 3.7
- PyCharm 2019.3
- Flask 1.1.1

### 简介

我们知道，每一次客户端向服务器发送`http`请求，服务器都会返回一个`http`状态码，如**200**就表示请求成功，**404**就表示访问的资源不存在。针对不同的`http`状态码，返回的`http`主体内容也不一样。

### Flask重定向

在`Flask`中，`Flask`对象提供了`redirect`方法来实现重定向。`redirect`方法的语法如下

```python
Flask.redirect(<location>,<status-code>, <response> )
```

其中

- location: 重定向的`url`
- status-code: `http`头部的状态码
- response: 响应实体

在实际场景中，`redirect`一般结合`url_for`来使用，而`url_for`会根据视图函数名称得到当前所指向的`url`

来看个实例

`login.html`文件内容

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Login</title>
</head>
<body>
    <form method = "post" action = "http://localhost:5000/validate">
        <table>
            <tr>
                <td>Email</td>
                <td><input type = 'email' name = 'email'></td>
            </tr>
            <tr>
                <td>Password</td>
                <td><input type = 'password' name = 'password'></td>
            </tr>
            <tr>
                <td><input type = "submit" value = "Submit"></td>
            </tr>
        </table>
    </form>
</body>
</html>
```

这是一个简单的登录界面，需要输入`email`和`password`来进行登录

`run.py`文件内容

```python
from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/validate', methods=['POST'])
def validate():
    if request.method == 'POST' and request.form['email'] == 'test@gmail.com' and request.form['password'] == 'test':
        return redirect(url_for('success'))
    return redirect(url_for('login'))

@app.route('/success')
def success():
    return 'Logged in successfully.'

if __name__ == '__main__':
    app.run(host="127.0.0.1",port=5000,debug=True)
```

主要看看服务器端对用户登录是的验证部分`validate`，当满足一定条件时，我们跳转到`success`视图函数所指定的`url`，否则，回到登录界面

启动`Flask`服务，访问http://127.0.0.1:5000/login

![flask](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F6a8b1ad546d0230a-e28029.png)

我们填入`email`为`test@gmail.com`，`password`为`test`

![flask](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fcc03fef707564a1c-80b31f.png)

如果`email`或`password`有一项错误的话，页面回到登录界面

![flask](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fb8e7fffd842b5fe4-78183d.png)