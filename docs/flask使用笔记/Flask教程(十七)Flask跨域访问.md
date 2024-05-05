# Flask教程(十七)Flask跨域访问

### 软硬件环境

- windows 10 64bit
- anaconda3 with [python](https://xugaoxiang.com/tag/python/) 3.7
- pycharm 2020.1.2
- [flask](https://xugaoxiang.com/tag/flask/) 1.1.2
- flask-restful 0.3.8
- flask-[cors](https://xugaoxiang.com/tag/cors/) 3.0.8

### 什么是跨域？

**跨域是指，浏览器从服务器`A`获取的静态资源，包括`html`、`css`、`javascript`，然后在`javascript`中通过`ajax`访问服务器`B`的静态资源或请求。**

### CORS

`w3c`组织制定了 `[Cross Origin Resource Sharing](https://www.w3.org/TR/cors/)` 的规范，简写为`CORS`，现在这个规范已经被大多数浏览器支持。

使用前一篇中的示例

```python
from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse


USERS = [
    {"name": "zhangsan"},
    {"name": "lisi"},
    {"name": "wangwu"},
    {"name": "zhaoliu"}
]

class Users(Resource):
    def get(self):
        return jsonify(USERS)

    def post(self):
        args = reqparse.RequestParser() \
            .add_argument('name', type=str, location='json', required=True, help="名字不能为空") \
            .parse_args()

        self.logger.debug(args)

        if args['name'] not in USERS:
            USERS.append({"name": args['name']})

        return jsonify(USERS)


app = Flask(__name__)
api = Api(app, default_mediatype="application/json")

api.add_resource(Users, '/users')

app.run(host='0.0.0.0', port=5001, use_reloader=True, debug=True)
```

前端页面`index.html`

```html
<html>
<body>

<button type="button" onclick="jump()">Click Me!</button>
<script>
    function jump(){
        let xhr = new XMLHttpRequest();
        xhr.open('GET', "http://192.168.1.210:5001/users", true);
        xhr.send();

        xhr.onreadystatechange = processRequest;

        function processRequest(e) {
            if (xhr.readyState == 4 && xhr.status == 200) {
                let response = JSON.parse(xhr.responseText);
                console.log(response)
            }
        }
    }
</script>
</body>
</html>
```

我们将`index.html`部署在一台机器上(192.168.1.140)，`flask`应用部署在另一台机器上(192.168.1.210)，然后在浏览器中访问`index.html`，点击页面中的按钮，这时候就会报错了

![flask-cors](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Ff64faf0bd9b4b04d-5d519b.png)

### flask配置[cors](https://xugaoxiang.com/tag/cors/)

`CORS`需要在后端应用中进行配置。在`flask`中，可以使用扩展`flask-cors`，首先安装

```python
pip install flask-cors
```

接下来来到`manage.py`，导入模块，并将`flask`应用包括起来就可以了，如下

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
```

重新启动应用，再次访问`index.html`，这时候，返回的结果就正常了

![flask-cors](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F8aa2aad1f7e32975-e0973c.png)