# flask01

django是个大而全的框架，flask是一个轻量级的框架

django内部为我们提供了非常多的组价，orm/session/cookie/admin/modelform/form/路由/视图/模版/中间件/分页/auth/contenttype/缓存/信号/多数据库连接

flask框架本身没有太多的功能，路由/视图/模版(jinja2)/session/中间件，第三方组件非常齐全

注意事项：

- django的请求处理是逐一封装和传递的
- flask的请求是利用上下文管理来实现的

## 今日概要

- flask的快速使用
- 实现一个管理系统
- 蓝图

## 今日详细

### 1.flask的基本使用

安装

```
pip install flask
```

flask本身是没有WSGI，是依赖于第三方的werkzeug实现的

重要的两个一个是werkzeug(`WSGI`)、一个是jinja2(`模版渲染`)

![image-20240503145601629](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240503145601629-3d821a.png)

#### 1.1 依赖wsgi Werkzeug

网站没有依赖flask，但是却执行起来了，虽然没有下面的功能(路由、视图等)

其实werkzeug就是充当了一个websocket的功能

```python
from werkzeug.serving import run_simple

def func(environ,start_response):
    print("请求来了")

if __name__ == '__main__':
    run_simple("127.0.0.1",5000,func)
```

![image-20240503150234513](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240503150234513-3e1fa1.png)

第二版本

```python
from werkzeug.serving import run_simple

class Flask(object):
    def __call__(self,environ,start_response):
        # 返回XXX类对象(执行flask源码功能)
        return XXX
    
app = Flask()

if __name__ == '__main__':
    # 将一个实例像函数一样调用，需要在类中实现__call__方法
    run_simple("127.0.0.1",5000,app)
```

第三个版本

```python
from werkzeug.serving import run_simple

class Flask(object):
    def __call__(self,environ,start_response):
        # 返回XXX类对象
        return XXX
    
    def run(self):
        # 将一个实例像函数一样调用，需要在类中实现__call__方法
        run_simple("127.0.0.1",5000,self)
    
app = Flask()

if __name__ == '__main__':
    app.run()
```

#### 1.2快速使用flask

```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "hello world"

if __name__ == '__main__':
    app.run()
```

![image-20240503150959036](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240503150959036-456647.png)

启动核心：和我们上面代码中推测的一样

![image-20240503151952034](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240503151952034-6f9c36.png)

![image-20240503152150062](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240503152150062-9843b8.png)

总结：

- flask框架是基于werkzeug的wsgi实现的，flask自己没有wsgi
- 用户请求一但到来，就会调用`app.__call__`方法
- 写flask的标准流程
  - 创建Flask对象
  - 路由和视图函数
  - app.run() 运行

#### 1.3用户登录 & 用户管理

- 渲染html页面

```python
from flask import Flask,render_template

app = Flask(__name__)


@app.route("/login")
def index():
    return render_template("login.html")


if __name__ == '__main__':
    app.run()
```

![image-20240503164400367](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240503164400367-8ff36c.png)

- 渲染json

```python
from flask import Flask,jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify({"code":1000,"data":"kets"})

if __name__ == '__main__':
    app.run()
```

![image-20240503164717451](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240503164717451-f9b2ff.png)

- 完整案例

```python
from flask import Flask,render_template,request,redirect

app = Flask(__name__)

@app.route("/login",methods=['GET',"POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    user = request.form.get("user")
    pwd = request.form.get("pwd")
    if user == "waws" and pwd == "123456":
        return redirect("/index")
    error_msg = "用户名或者密码错误"
    return render_template("login.html",error=error_msg)

@app.route("/index")
def index():
    return "首页"

if __name__ == '__main__':
    app.run()
```

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Killer-89757</title>
</head>
<body>
  <h1>用户登录界面</h1>
  <form method="post">
      <input type="text" name="user"></input>
      <input type="text" name="pwd"></input>
      <input type="submit" value="提交"> <span style="color: red">{{error}}</span>
  </form>
</body>
</html>
```

![image-20240503174713515](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240503174713515-b17079.png)

获取查询字符串的两种方式：

- 第一种使用 `request.args.get` 去获得

```python
@app.route("/edit")
def edit():
    nid = request.args.get("nid")
    print(nid)
    return "编辑"
```

- 第二种使用`<int:nid>` 加上handler传参的方式去获得，并将参数转化成int类型，不加就是字符串类型

```python
# nid是字符串类型
@app.route("/del/<nid>")
def delete(nid):
    print(nid)
    return "删除"

# nid是int类型
@app.route("/del/<int:nid>")
def delete(nid):
    print(nid)
    return "删除"
```

url的跳转方式有两种：

```python
@app.route("index",endpoint="idx")
def index()：
	pass

def a():
    # 直接使用redirect + 路由的方式跳转
    return redirct("/index")

def b():
    # 使用redirect + url_for + endpoint别名的方式进行跳转
    return rediect(url_for("idx"))
```

项目完整代码

```python
from flask import Flask,render_template,request,redirect,url_for

app = Flask(__name__)

data_dict = {
    "1":{"name":"狗剩",'age':18,"gender":"男"},
    "2":{"name":"钢蛋",'age':20,"gender":"女"},
    "3":{"name":"铁锤",'age':40}
}

@app.route("/index",endpoint='idx')
def index():
    return render_template("index.html",data_dict=data_dict)

@app.route("/edit",methods=["GET","POST"])
def edit():
    # 拿到的都是字符串类型
    nid = request.args.get("nid")

    if request.method =="GET":
        info = data_dict[nid]
        return render_template("edit.html",info=info)
    user = request.form.get('name')
    age = int(request.form.get('age'))
    gender = request.form.get("gender")
    data_dict[nid]["name"] = user
    data_dict[nid]["age"] = age
    data_dict[nid]["gender"] = gender
    return redirect(url_for("idx"))

@app.route("/del/<nid>")
def delete(nid):
    del data_dict[nid]
    print("删除成功")
    return redirect(url_for('idx'))

if __name__ == '__main__':
    app.run()
```

html文件

```html
// edit.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>
  <h1>修改用户信息</h1>
  <form method="post">
    <input type="text" name="name" value="{{ info.name }}">
    <input type="text" name="age" value="{{ info.age }}">
    <input type="text" name="gender" value="{{ info.gender }}">
    <input type="submit" value="提交">
  </form>
</body>
</html>

// index.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>
  <h1>用户信息列表</h1>
  <table border="1">
    <thead>
      <tr>
        <th>ID</th>
        <td>姓名</td>
        <td>年龄</td>
        <td>性别</td>
        <td>操作</td>
      </tr>
    </thead>
    <tbody>
      {% for key,value in data_dict.items() %}
        <tr>
          <td>{{  key  }}</td>
          <td>{{  value.name  }}</td>
          <td>{{  value["age"]  }}</td>
          <td>{{  value.get("gender","男")  }}</td>
          <td>
            <a href="/edit?nid={{key}}">编辑</a>
            <a href="/del/{{key}}">删除</a>
          </td>
        </tr>
      {% endfor %}
    </tbody>
  </table>
</body>
</html>
```

总结：

- flask的路由使用的就是装饰器‘
- 路由参数 `路径参数`、`endpoint`、`methods`
  - endpoint不能重名、**endpoint不写默认和handler同名**
- 使用动态路由
- 提交数据
  - request.args
  - request.form

- 返回数据
  - render_template("模板文件")
  - render.jsonify()
  - render.redirect('/index')   render.redirect(url_for('idx'))
  - return "我是waws"

- 模板处理

  - {{  name }}

  - ```python
    {% for key,value in term.items() %}
    	{{ key }}
        {{ value }}
    {% endfor %}
    ```

在jinja2中使用注释，不能直接使用html的！的方式

```python
<!--          <td>{{  key  }}</td>-->    # 不会生效
{# <td>{{  key  }}</td> #}    # 生效
```

#### 1.4 保存用户的登录信息

![image-20240503184306292](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240503184306292-550aa8.png)

```python
from flask import Flask,render_template,request,redirect,session

app = Flask(__name__)
app.secret_key = "1233467890rtyuiopvbnm"

@app.route("/login",methods=['GET',"POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    user = request.form.get("user")
    pwd = request.form.get("pwd")
    if user == "waws" and pwd == "123456":
        session['xxx'] = 'waws'
        return redirect("/index")
    error_msg = "用户名或者密码错误"
    return render_template("login.html",error=error_msg)


@app.route("/index")
def index():
    return "首页"

if __name__ == '__main__':
    app.run()
```

flask的session信息在服务端不存储，而是通过加密的方式放在浏览器段进行存储

![image-20240503184455226](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240503184455226-9967c9.png)

关于装饰器的小插曲

- 使用functools改变装饰器指向

```python
def auth(func):
    def inner(*args,**kwargs):
        return func(*args,**kwargs)
    return inner

@auth
def login():
    pass

print(login.__name__)

"""
inner
"""
-----------------------
# 可以使用functools改变装饰器指向
import functools
def auth(func):
    @functools.wraps(func)
    def inner(*args,**kwargs):
        return func(*args,**kwargs)
    return inner

@auth
def login():
    pass

print(login.__name__)
"""
login
"""
```

- 多个装饰器的执行顺序

```python
# 离函数最近的装饰器最先执行，由内向外
import functools
def auth1(func):
    print("auth1")
    @functools.wraps(func)
    def inner(*args,**kwargs):
        return func(*args,**kwargs)
    return inner


def auth0(func):
    print("auth0")
    @functools.wraps(func)
    def inner(*args, **kwargs):
        return func(*args, **kwargs)
    return inner

@auth0
@auth1
def login():
    pass

login()
"""
auth1
auth0
"""
```

实际上被包裹上之后，执行的函数变成了inner，但是名字还是login

上面引入@functools.wraps(func)实际上是要解决路由-inner冲突问题，具体如下：

![image-20240503194803547](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240503194803547-e00246.png)

请求任意一个接口都需要session的状态

```python
from flask import Flask,render_template,request,session,redirect,url_for
import functools

app = Flask(__name__)
app.secret_key = "013uherwengnkwdgnkwn"

def auth(func):
    @functools.wraps(func)
    def inner(*args,**kwargs):
        username = session.get('xxx')
        if not username:
            return redirect(url_for('login'))
        return func(*args,**kwargs)
    return inner

@app.route("/login",methods=['GET',"POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    user = request.form.get("user")
    pwd = request.form.get("pwd")
    if user == "waws" and pwd == "123456":
        session['xxx'] = 'waws'
        return redirect("/index")
    error_msg = "用户名或者密码错误"
    return render_template("login.html",error=error_msg)

@app.route("/edit")
@auth
def edit():
    return 'edit'

@app.route("/del")
@auth
def delete():
    return "删除"

@app.route("/index")
@auth
def index():
    return "首页"

if __name__ == '__main__':
    app.run()
```

### 2.蓝图

帮助我们构建一个业务功能可拆分的目录结构

- 项目
  - 文件
    - templates
    - static
    - views(视图)
      - killer.py
      - waws.py
    - `__init__.py`
  - manage.py （启动文件）

```python
# __init__.py
from flask import Flask
from .views.killer import killer
from .views.waws import waws

def create_app():
    app = Flask(__name__)
    app.secret_key = "jdoasfajkfpafkadsf"

    @app.route('/index')
    def index():
        return 'index'

    # 注册蓝图
    # 请求加上前缀 http://127.0.0.1:5000/killer/f2
    app.register_blueprint(killer,url_prefix='/killer')
    app.register_blueprint(waws,url_prefix='/waws')

    return app

# manage.py
from flask_project import create_app

app = create_app()

if __name__ == '__main__':
    app.run()
    
# killer.py
from flask import Blueprint

killer = Blueprint('killer',__name__)

@killer.route('/f1')
def f1():
    return 'killer-f1'

@killer.route('/f2')
def f2():
    return 'killer-f2'

# waws.py
from flask import Blueprint

waws = Blueprint('waws',__name__)

@waws.route('/f3')
def f1():
    return 'waws-f3'

@waws.route('/f4')
def f2():
    return 'waws-f4'
```

> 面试题：django的app和flask的蓝图有什么区别？