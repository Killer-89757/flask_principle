# Flask教程(二十五)接收多文件

## 环境

- windows 10 64bit
- anaconda3 with python 3.7
- flask 1.1.2

## 前言

`web` 后端接收多文件，在实际项目中也算是个常见的需求，本文就来看看，在 `flask` 中如何来实现这个需求。

## 实例

先来看后端代码，少量注释写在了代码中

```python
from flask import Flask, request, jsonify
app = Flask(__name__)
@app.route('/upload', methods=['POST'])
def index():
    # 使用request模块接收带对应标签的文件列表，这里对应图片和视频
    image_files = request.files.getlist('image')
    video_files = request.files.getlist('video')
    # 判断是否有空文件
    if not image_files and not video_files:
        return jsonify({
            "code": -1,
            "message": "No upload images or videos."
        })
    # 从文件列表依次取出并保存，文件名与上传时一致
    for image_file in image_files:
        image_file.save(image_file.filename)
    # 同上
    for video_file in video_files:
        video_file.save(video_file.filename)
    return jsonify({
        "code": 0,
        "message": "upload images and videos success."
    })
if __name__ == '__main__':
    # 启动flask app
    app.run('0.0.0.0', debug=True, port=5000)
```

示例代码就这么简单，写完后，保存，启动服务

```
python app.py
```

客户端部分，这里使用 `postman` 这个工具来进行模拟请求，打开 `postman`，新建一个请求，在 `Body` 里面携带参数，选择 `form-data`。

鼠标点击 `key` 值尾部，出现 `Text` 和 `File` 两种类型，这里我们选择 `File`，这里我们需要2个 `key` 值，分别是 `image` 和 `video`，这2个值在 `flask` 中会用到，2者匹配起来就可以了，你想写其它的字符都可以

![flask receive multiple files](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F87203849ca9152d4-01f5bc.webp)

准备就绪后，就可以点击发送了，成功后，在响应部分，可以看到返回值 `json` 数据

![flask receive multiple files](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fdf72d10df6e152c9-ec26d3.webp)

同时，在 `flask` 后端，也成功接收并保存了对应的图片文件和视频文件，文件名与上传时的文件名保持一致

![flask receive multiple files](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F9b19f97d48c35b2e-60c9b3.webp)