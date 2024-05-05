# Flask教程(二十一)添加favicon

### 软硬件环境

- windows 10 64bit
- anaconda3 with [python](https://xugaoxiang.com/tag/python/) 3.7
- [flask](https://xugaoxiang.com/tag/flask/) 1.1.2

### 前言

`favicon`是`favorites icon`的缩写，是指在网页浏览器显示在标签页或者历史记录里的图标。这个图标能帮助用户将您的网站与其他网站区分开。

![favicon](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F7935912149734132-8edfbe.png)

### 图片转icon

`favicon`文件的尺寸通常比较小，常见的尺寸有16x16，32x32和48x48。我们准备一张`jpg`或者`png`的图片，来到在线的转换站点进行转换

https://favicon.io/favicon-converter/

![favicon](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F97f22b79c104aa15-b347e6.png)

### flask中如何处理？

我们简单写个`flask`应用，这个应该非常熟练了，`app.py`内容为

```python
from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
```

创建模板文件`index.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <link rel="shortcut icon" href="{{ url_for('static', filename='favicon.ico') }}">
    <title>Favicon</title>
</head>
<body>
    <p>Hello favicon</p>
</body>
</html>
```

然后将转换好的`icon`文件放到`static`文件夹下，文件名为`favicon.ico`

最后启动`flask`服务后，访问`http://127.0.0.1:5000`，在浏览器地址栏左侧就可以看到`favicon`了

![favicon](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fe5bc8003b837731d-2e2961.png)