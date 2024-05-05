# Flask教程(四)模板

### 软硬件环境

- Windows 10 64bit
- Anaconda3 with [python](https://xugaoxiang.com/tag/python/) 3.7
- PyCharm 2019.3
- Flask 1.1.1

### 前言

在前面的教程中，我们的页面只是显示了一些简单的字符，还没有使用到`html`的各种元素，本节开始学习`Flask`当中的模板，来创建更加复杂、更加美观的网页。

### 在视图函数中使用html

先来看个实例

```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return '<html><body><h1>Hello flask!</h1></body></html>'

if __name__ == '__main__':
    app.run(host="127.0.0.1",port=5000,debug=True)
```

在视图函数`index`中，返回的是一个`html`的字符串，标签`<h1>`表示的是一级标题，访问`http://127.0.0.1:5000`，可以看到标题版的`Hello flask!`

![flask](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F20d4e087a4aab20c-524ae5.png)

但是考虑到实际的网页内容都很复杂，把`html`都写在视图函数里显然是不现实的，这个时候模板就出现了。

### 模板的使用

`Flask`提供了`Jinja2`模板引擎，它可以渲染外部的`html`网页文件，对应的函数是`render_template`，看下面这个例子

```python
from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host="127.0.0.1",port=5000,debug=True)
```

接下来我们在工程下创建一个文件夹`templates`(`Flask`默认存放`html`文件的地方，`static`存放静态文件，如`js`、`css`、图片等)，然后在文件夹下新建`index.html`，输入下面的代码

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Index</title>
</head>
<body>
    <h1>Hello flask!</h1>
</body>
</html>
```

访问`http://127.0.0.1:5000`，可以看到标题是`Index`，内容是`Hello flask!`，同时也可以通过浏览器去查看网页的源代码，内容跟上面的`index.html`文件是一样的

![flask](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fcc37314ddaaed371-84c31d.png)

![flask](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F9951494d6e6f7777-17b1ce.png)

接下来就有个问题了，既然`html`内容已经独立出来了，怎么将数据通过视图传递到模板文件呢？来看下面这个实例

`index.html`文件内容

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Index</title>
</head>
<body>
    <h1>Hello {{ name }}!</h1>
</body>
</html>
```

`run.py`则变成

```python
from flask import Flask, render_template
app = Flask(__name__)

@app.route('/<name>')
def index(name):
    return render_template('index.html', name=name)

if __name__ == '__main__':
    app.run(host="127.0.0.1",port=5000,debug=True)
```

可以看到我们在`html`文档中使用了`{{ name }}`这条语句，这是`Jinja2`模板中的定界符，这个`name`就是视图传递过来的数据。常用的定界符有如下几个

- {% ... %} 代表这是语句块
- {{ ... }} 获取表达式的值
- {# ... #} 代表注释

来到视图部分，我们接受`URL`传递过来的数据，然后通过`render_template`传递给`html`文档

最后程序执行的效果如下

![flask](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F9d7fbb316cb776cb-f53b44.png)