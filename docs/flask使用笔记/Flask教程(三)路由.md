# Flask教程(三)路由

### 软硬件环境

- Windows 10 64bit
- Anaconda3 with [python](https://xugaoxiang.com/tag/python/) 3.7
- PyCharm 2019.3
- Flask 1.1.1

### 什么是路由

路由(`Routing`)是用来映射`URL`和执行对应任务的函数。通过设置不同的路由，来访问不同的页面，像[上一节](./Flask教程(二)第一个Flask应用程序.md)中的`/`路由，就是访问网站的根目录。

### 实例

下面来看一个实例

```python
from flask import Flask
app = Flask(__name__)

@app.route('/home')
def index():
    return "Welcome to home!"

if __name__ == '__main__':
    app.run(host="127.0.0.1",port=5000,debug=True)
```

这时候去访问`http://127.0.0.1:5000`就会出现404错误

![flask](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fdd20455d4d54294d-8a5e82.png)

因为我们代码里根本就没有处理`/`路由的请求，访问`http://127.0.0.1:5000/home`，页面才会显示`Welcome to home!`

![flask](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F1824e088335d2354-18f43b.png)

那么另一个问题来了，如果有多条路由，比如`/home/shelly`、`/home/tom`和`、/home/carl`，能不能在同一个函数中进行处理呢？答案是可以的，我们可以通过给`@app.route`传递变量的方式实现，如下

```python
from flask import Flask
app = Flask(__name__)

@app.route('/home/<name>')
def index(name):
    return f"Welcome to home!{name}"

if __name__ == '__main__':
    app.run(host="127.0.0.1",port=5000,debug=True)
```

这时候访问`http://127.0.0.1:5000/home/carl`，页面上就会显示`Welcome to home!carl`；访问`http://127.0.0.1:5000/home/shelly`，页面上就会显示`Welcome to home!shelly`了

![flask](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F25ac448aad31d2aa-259d03.png)

![flask](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F7b5d857af847d8d8-cd9a87.png)

可以看到上面的实例中，传递的参数是字符串类型，那如果是其它数据类型，怎么办呢？看下面这个实例

```python
from flask import Flask
app = Flask(__name__)

# 特别注意，int后面冒号前后不能有空格
@app.route('/home/<int:age>')
def index(age):
    return 'Age={}'.format(age)

if __name__ == '__main__':
    app.run(host="127.0.0.1",port=5000,debug=True)
```

这个时候我们就可以传递整型数据了 ，比如`http://127.0.0.1:5000/home/20`

![flask](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F52dfa4722eb616ad-7d421e.png)

除了上述添加路由的方法，`Flask`还提供了一个函数`add_url_rule`，它也能够完成同样的功能，看个实例

```python
from flask import Flask
app = Flask(__name__)

def index():
    return 'Hello flask!'

app.add_url_rule('/', "index", index)

if __name__ == '__main__':
    app.run(host="127.0.0.1",port=5000,debug=True)
```

访问`http://127.0.0.1:5000`，可以看到页面显示`Hello flask!`，效果跟使用`@app.route`是一模一样的

![flask](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F81b923b1e9af5052-f837ff.png)