# Flask教程(二十四)请求转发

### 软硬件环境

- windows 10 64bit
- anaconda3 with python 3.7
- [flask](https://xugaoxiang.com/tag/flask/) 1.1.2

### 前言

在某些情况下，我们需要在`flask`中进行`http`请求的转发，也就是让`flask`成为`http`代理。本文借助流行的`http`请求库`requests`来实现。

### 代码示例

```python
from flask import Flask
import requests

app = Flask(__name__)


@app.route('/')
def index():
    # 这里可以使用requests.request来实现各种http方法
    req = requests.get('http://127.0.0.1:5000/proxy')
    # 响应体返回，这里是字符串
    return req.text


@app.route('/proxy')
def proxy():
    return "Hello Flask."


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000,debug=True)
```

启动服务，访问`http://127.0.0.1:5000`，页面上会显示字符串`Hello Flask.`

![flask_proxy](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F6d1bee8c61840904-0e97ba.png)