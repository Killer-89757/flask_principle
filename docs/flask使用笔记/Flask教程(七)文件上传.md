# Flask教程(七)文件上传

### 软硬件环境

- Windows 10 64bit
- Anaconda3 with [python](https://xugaoxiang.com/tag/python/) 3.7
- PyCharm 2019.3
- Flask 1.1.1

### 简介

文件上传是个经常碰到的问题。其中涉及很多的内容比如文件的上传、文件类型的过滤，文件大小的限制，文件重命名，文件目录管理等等。下面我们来看看最基本的上传功能的实现，至于提到的其它问题，大家可以自己摸索摸索。

### Flask处理文件上传

在`Flask`中进行文件上传，需要在通过`html`中的`form`表单，而且需要设置`enctype=multipart/form-data`，看下面的实例

`index.html`文件内容

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>upload</title>
</head>
<body>
    <form action = "/success" method = "post" enctype="multipart/form-data">
        <input type="file" name="file">
        <input type = "submit" value="Upload">
    </form>
</body>
</html>
```

主要就是一个`form`表单，使用的`http`方法是`POST`并且设置`enctype="multipart/form-data"`，`input`标签的类型是`file`，接下来还需要编写一个`html`，用来显示上传成功后的信息

`success.html`文件内容

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Success</title>
</head>
<body>
    <p>File uploaded successfully!</p>
    <p>File Name: <b> {{name}} </b></p>
</body>
</html>
```

最后来看看`Flask`端的处理代码，`run.py`文件内容

```python
from flask import Flask, render_template, request
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/success', methods=['POST'])
def success():
    if request.method == 'POST':
        f = request.files['file']
        f.save(f.filename)
        return render_template('success.html', name=f.filename)


if __name__ == '__main__':
    app.run(host="127.0.0.1",port=5000,debug=True)
```

注意到`success`方法中，只处理`POST`请求，并从请求对象中的`files`获取到文件的内容，调用`save`保存文件，渲染网页时，将文件名传递过去，文件名会在`success.html`中显示

启动`Flask`服务，访问[http://127.0.0.1:5000](http://127.0.0.1:5000/)

![flask](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F92777c31881f0a5f-4424de.png)

点击`选择文件`，在弹出框中选择需要上传的文件，然后点击`Upload`

![flask](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F3b3cc78a98b70938-0f822b.png)

来到`pycharm`可以看到刚刚接收到的文件`python_logo.png`

![flask](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fa3ee8dded624982b-52c725.png)

