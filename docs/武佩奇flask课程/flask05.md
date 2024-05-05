# flask05

## 内容补充

1. wsgi的本质：socket服务端
2. 单利模式（基于文件导入实现）

3. 从看flask源码你学到了什么？

```
- 新的编程思路。
	- django、drf数据是通过传递。
	- flask，存储在某个地方，以后用的时候去拿。 
	哪种好？两个不同的实现机制，没有好坏之分。
	django好，疑问如果是一个初学者对于django的机制比较好理解，flask学习代价比较大（了解上下文管理职机制之后才能更好的理解）。
    
- 技术点
	- 单例模式的应用场景
	- LocalProxy
	- 装饰器不注意functools
```

4. 在flask的Local对象中为什么要通过线程ID进行区分？

```
因为在flask中可以开启多线程的模式，当开启多线程模式进行处理用户请求时，需要将线程之间的数据进行隔离，以防止数据混乱。
```

5. 在flask的Local对象中为什么要维持成一个栈？

```
{
	111:{stack:[ctx, ]},
}
```

```
在web runtime 时，栈永远只有1个对象。
    {
        111:{stack:[ctx, ]}
        112:{stack:[ctx, ]}
    }
    {
        111:{stack:[app_ctx, ]}
        112:{stack:[app_ctx, ]}
    }
```

```python
在写离线脚本时，才会用在栈中放多个对象。 （创建一个py文件本地运行）

# 注意这个时候的current_app对象
from flask import current_app, g, Flask

def create_app():
    app = Flask(__name__)

    @app.route('/index')
    def index():
        return 'index'

    return app


app1 = create_app()
with app1.app_context():  # AppContext对象(app,g) -> local对象
    print(current_app.config)  # -1 top app1
    app2 = create_app()
    with app2.app_context():  # AppContext对象(app,g) -> local对象
        print(current_app.config)  # top -1 app2
    print(current_app.config)  # top -1 app1

if __name__ == '__main__':
    app1.run()

写离线脚本且多个上下文嵌套时，才会在栈中添加多个app对象。
```

注意：在flask中很少出现嵌套的脚本。

![image-20240505132812642](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240505132812642-5a1459.png)

## 今日概要

- 信号
- flask-script组件
- 蓝图

## 今日详细

### 1. 信号（源码）

信号，是在flask框架中为我们预留的钩子，让我们可以进行一些自定义操作。

```
pip3 install blinker 
```

根据flask项目的请求流程来进行设置扩展点

- 中间件

  ```python
  from flask import Flask,render_template
  
  app = Flask(__name__)
  
  
  @app.route('/index')
  def index():
      return render_template('index.html')
  
  
  @app.route('/order')
  def order():
      return render_template('order.html')
  
  
  class MyMiddleware(object):
      def __init__(self,old_app):
          self.wsgi_app = old_app.wsgi_app
  
      def __call__(self, *args, **kwargs):
          print('123')
          result = self.wsgi_app(*args, **kwargs)
          print('456')
          return result
  
  app.wsgi_app = MyMiddleware(app)
  
  if __name__ == '__main__':
      app.run()
  ```

- appcontext_pushed

  - 当app_ctx被push到local中栈之后，会触发appcontext_pushed信号，之前注册在这个信号中的方法，就会被执行。

  ![image-20240505135106110](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240505135106110-98927d.png)

  ```python
  from flask import Flask,render_template
  from flask import signals
  
  app = Flask(__name__)
  
  @signals.appcontext_pushed.connect
  def f1(arg):
      print('appcontext_pushed信号f1被触发',arg)
  
  @signals.appcontext_pushed.connect
  def f2(arg):
      print('appcontext_pushed信号f2被触发',arg)
  
  @app.route('/index')
  def index():
      return "index"
  
  @app.route('/order')
  def order():
      return "order"
  
  if __name__ == '__main__':
      app.run()
      # app.__call__
  
  ```

  ![image-20240505135304048](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240505135304048-bbe11c.png)

- 执行before_first_request扩展

  ```python
  from flask import Flask,render_template
  
  app = Flask(__name__)
  
  @app.before_first_request
  def f2():
      print('before_first_requestf2被触发')
  
  @app.route('/index')
  def index():
      return "index"
  
  @app.route('/order')
  def order():
      return "order"
  
  if __name__ == '__main__':
      app.run()
  ```

  ![image-20240505135604852](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240505135604852-80798e.png)

- request_started信号

  ```python
  from flask import Flask,render_template
  from flask import signals
  app = Flask(__name__)
  
  @signals.request_started.connect
  def f3(arg):
      print('request_started信号被触发',arg)
  
  @app.route('/index')
  def index():
      return "index"
  
  @app.route('/order')
  def order():
      return "order"
  
  if __name__ == '__main__':
      app.run()
  ```

  ![image-20240505135720482](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240505135720482-3d2288.png)

- url_value_processor

  - 在请求之前被触发

  ```python
  from flask import Flask,render_template,g
  from flask import signals
  app = Flask(__name__)
  
  
  @app.url_value_preprocessor
  def f5(endpoint,args):
      print('f5')
  
  @app.route('/index')
  def index():
      print('index')
      return "index"
  
  @app.route('/order')
  def order():
      print('order')
      return "order"
  
  if __name__ == '__main__':
      app.run()
  ```

- before_reuqest

  ```python
  from flask import Flask,render_template,g
  from flask import signals
  app = Flask(__name__)
  
  @app.before_request
  def f6():
      g.xx = 123
      print('f6')
  
  @app.route('/index')
  def index():
      print('index')
      return "index"
  
  @app.route('/order')
  def order():
      print('order')
      return "order"
  
  if __name__ == '__main__':
      app.run()
  ```

  ![image-20240505140400014](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240505140400014-dc2c13.png)

- 视图函数

- before_render_template / rendered_template

  ```python
  from flask import Flask,render_template,g
  from flask import signals
  app = Flask(__name__)
  
  @signals.before_render_template.connect
  def f7(app, template, context):
      print('before_render_template f7 被触发')
  
  @signals.template_rendered.connect
  def f8(app, template, context):
      print('template_rendered f8 被触发')
  
  @app.route('/index')
  def index():
      return render_template("index.html")
  
  @app.route('/order')
  def order():
      return render_template("order.html")
  
  if __name__ == '__main__':
      app.run()
  ```

  ![image-20240505140904216](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240505140904216-35c026.png)

- after_request

  ```python
  from flask import Flask,render_template,g
  from flask import signals
  app = Flask(__name__)
  
  @app.after_request
  def f9(response):
      print('after_request f9 被触发')
      return response
  
  @app.route('/index/')
  def index():
      return render_template('index.html')
  
  @app.route('/order')
  def order():
      print('order')
      return render_template('order.html')
  
  if __name__ == '__main__':
      app.run()
  ```

- request_finished

  ```python
  from flask import Flask,render_template,g
  from flask import signals
  app = Flask(__name__)
  
  @signals.request_finished.connect
  def f10(app,response):
      print('request_finished f10 被触发')
  
  @app.route('/index/')
  def index():
      return render_template('index.html')
  
  @app.route('/order')
  def order():
      print('order')
      return render_template('order.html')
  
  if __name__ == '__main__':
      app.run()
  ```

- got_request_exception

  ```python
  from flask import Flask,render_template,g
  from flask import signals
  app = Flask(__name__)
  
  @app.before_first_request
  def test():
      int('asdf')
  
  @signals.got_request_exception.connect
  def f11(app,exception):
      print('got_request_exception f11 被触发')
  
  @app.route('/index/')
  def index():
      return render_template('index.html')
  
  @app.route('/order')
  def order():
      print('order')
      return render_template('order.html')
  
  if __name__ == '__main__':
      app.run()
  ```

  ![image-20240505141301362](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240505141301362-5b144d.png)

- teardown_request

  ```python
  from flask import Flask,render_template,g
  from flask import signals
  app = Flask(__name__)
  
  @app.teardown_request
  def f12(exc):
      print('teardown_request f12 被触发')
  
  @app.route('/index/')
  def index():
      return render_template('index.html')
  
  @app.route('/order')
  def order():
      print('order')
      return render_template('order.html')
  
  if __name__ == '__main__':
      app.run()
  ```

- request_tearing_down

  ```python
  from flask import Flask,render_template,g
  from flask import signals
  app = Flask(__name__)
  
  @signals.request_tearing_down.connect
  def f13(app,exc):
      print('request_tearing_down f13 被触发')
  
  @app.route('/index/')
  def index():
      return render_template('index.html')
  
  @app.route('/order')
  def order():
      print('order')
      return render_template('order.html')
  
  if __name__ == '__main__':
      app.run()
  ```

- appcontext_popped

  ```python
  from flask import Flask,render_template,g
  from flask import signals
  app = Flask(__name__)
  
  @signals.appcontext_popped.connect
  def f14(app):
      print('appcontext_popped f14 被触发')
  
  @app.route('/index/')
  def index():
      return render_template('index.html')
  
  @app.route('/order')
  def order():
      print('order')
      return render_template('order.html')
  
  if __name__ == '__main__':
      app.run()
  ```

总结：关于flask内部共有14+个扩展点用于我们对flask框架内部进行定制，其中有：9个是信号。

```python
template_rendered = _signals.signal("template-rendered")
before_render_template = _signals.signal("before-render-template")
request_started = _signals.signal("request-started")
request_finished = _signals.signal("request-finished")
request_tearing_down = _signals.signal("request-tearing-down")
got_request_exception = _signals.signal("got-request-exception")
appcontext_tearing_down = _signals.signal("appcontext-tearing-down")
appcontext_pushed = _signals.signal("appcontext-pushed")
appcontext_popped = _signals.signal("appcontext-popped")

message_flashed = _signals.signal("message-flashed")
```

#### 扩展:flash 

flash存值之后只能取一次

![image-20240505144612849](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240505144612849-3632e9.png)

```python
from flask import Flask,render_template,flash,get_flashed_messages,session
from flask import signals
app = Flask(__name__)
app.secret_key = 'iuknsoiuwknlskjdf'

@app.route('/index/')
def index():
    # flash('123')
    session['k1'] = 123
    return render_template('index.html')

@app.route('/order')
def order():
    # messages = get_flashed_messages()
    # print(messages)
    val = session['k1']
    del session['k1']
    print(val)
    return render_template('order.html')

if __name__ == '__main__':
    app.run()
```

![image-20240505145136404](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240505145136404-7bf06f.png)

### 2.flask-script

flask的组件，用于运行flask程序。 

- 安装

  ```python
  pip3 install flask-script
  ```

- 使用
  ![image-20240505151441728](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240505151441728-f00fe0.png)

- 其他执行命令

  ```python
  from s24day95 import create_app
  from flask_script import Manager
  
  app = create_app()
  manager = Manager(app)
  
  @manager.command
  def custom(arg):
      """
      自定义命令
      python manage.py custom 123
      :param arg:
      :return:
      """
      print(arg)
  
  @manager.option('-n', '--name', dest='name')
  @manager.option('-u', '--url', dest='url')
  def cmd(name, url):
      """
      自定义命令
      执行： python manage.py  cmd -n waws -u http://www.baidu.com
      :param name:
      :param url:
      :return:
      """
      print(name, url)
  
  if __name__ == '__main__':
      manager.run()
  ```

![image-20240505152335546](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240505152335546-021cdc.png)

- 其他

  ```
  结合：flask-migrate / flask-sqlalchemy
  
  python manage.py migrate 
  ```

### 3.蓝图

目录结构的划分

- 分功能蓝图(项目大)

  ```python
  - waws_project(项目)
  	- waws_project(蓝图)
      	- user（用户功能）
          	- static
              - templates
              	- add_user.html 
              - views
              	- add_user.py
                  - remove_user.py
              - __init__.py
  		- power（权限功能）
          	- static
              - templates
              - views
              	- add_power.py
                  - remove_power.py
              - __init__.py
          - ......
      	- __init__.py
      - config
      	- settings.py
      - manage.py
  ```

  ```python
  # user/__init__.py文件
  from flask import Blueprint,render_template
  
  # 蓝图中视图函数render_template默认会去蓝图根目录找模板文件,没有在去功能蓝图的templates下查找
  user = Blueprint('user',__name__,template_folder='templates')
  
  # 因为是从manage.py启动的文件，所以在注册蓝图的时候可以走到当前文件，但是无法和视图函数进行关联，所以需要在这个地方引入才行
  from .view import add_user
  
  # waws_project/__init__.py文件
  from flask import Flask
  
  def create_app():
      app = Flask(__name__)
      app.config.from_object('config.settings')
  
      from .user import user
      from .power import power
  
      app.register_blueprint(user)
      app.register_blueprint(power)
  
      return app
  
  # view/add_user.py
  from .. import user
  from flask import render_template
  
  @user.route("/add_user")
  def add_user():
  	return render_template("add_user.html")
  ```

- 分结构蓝图(项目中、小)

  ```python
  - waws_project(项目)
  	- waws_project(蓝图)
      	- static
          - templates
          	- add_user.html 
          - views
          	- add_user.py
              - remove_user.py
          - __init__.py
      - config
      	- settings.py
      - manage.py
  ```

  















































