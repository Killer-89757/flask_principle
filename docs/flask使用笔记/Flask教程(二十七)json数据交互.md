# Flask教程(二十七)json数据交互

## 环境

- windows 10 64bit
- anaconda3 with python 3.8.11
- flask 2.2.2

## 前言

`json` 是模块间数据传输最常见的方法，`flask` 同样能够很方便的接收和返回 `json` 格式的数据。

## 实操

来看完整的服务端代码，这里使用 `flask.request` 中的 `get_json` 方法

```python
from flask import Flask, jsonify, request
app = Flask(__name__)
@app.route('/', methods=['POST'])
def post():
    # 获取请求的json数据
    req_json = request.get_json()
    print(req_json)
    # 对接收到的数据进行简单处理
    if req_json["operatorID"] != "0001":
        return jsonify({"error": "error."})
    dict_ret = {}
    dict_ret["responseType"] = 2
    dict_ret["status"] = 1000
    dict_ret["num"] = 1
    dict_ret["MD5"] = "4F3D2A1E"
    return jsonify(dict_ret)
if __name__ == '__main__':
    # 启动服务
    app.run(host='0.0.0.0', port=80, debug=True)
```

然后，启动服务。我们使用 `postman` 这个工具来模型客户端请求

![flask json](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fc48cdcff67592b70-a68a61.webp)

`postman` 发送请求后，可以得到响应，响应数据也是一个 `json`

![flask json](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fb0723731aa0ed3c1-a7b66c.webp)

如果请求 `json` 中 `operatorID` 不是 0001，服务端则返回 `error`

![flask json](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Ff2155f2e04c665fc-83448a.webp)

如果需要编程来实现请求，可以借助于 [requests](https://xugaoxiang.com/2020/11/28/python-module-requests/) 这个库

```python
import requests

r_json = {
    "name": "xgx",
    "operatorID":"0001",
    "requestType":1,
    "num":1
}

r_headers = {"Content-type": "application/json"}
r = requests.post('http://127.0.0.1', json=r_json, headers=r_headers)
print(r.status_code)
print(r.json())
```

