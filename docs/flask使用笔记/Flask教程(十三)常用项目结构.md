# Flask教程(十三)常用项目结构

### 软硬件环境

- windows 10 64bit
- anaconda3 with [python](https://xugaoxiang.com/tag/python/) 3.7
- pycharm 2020.1.2
- [flask](https://xugaoxiang.com/tag/flask/) 1.1.2

### 前言

前面的内容，在我们的示例中，除了模板文件以外，其它的`python`代码都是写在了同一个`py`文件当中，这里面包含了视图函数、数据库模型、应用的配置等等。在小的示例中，这样写问题不大，但是在实际项目中，这样肯定是不行的。

### 项目结构

`Flask`是一个轻量级的`Web`框架，扩展性强，灵活性高，容易上手，不过`Flask`并没有给出明确的项目结构，而是让开发者根据实际需求，创建适合自己的项目结构。需要说明的是本文所介绍的项目结构可能并不是最好的，仅仅是一个参考，不同的项目，不同的团队，不同的理念，会有不同的项目结构

```python
project/
  forms/
    myform.py
    ...
  models/
    __init__.py
    mymodel.py
    ...
  routes/
    __init__.py
    myroute.py
    ...
  static/
    ...
  services/
    __init__.py
    ...
  templates/
    index.html
    ...
  __init__.py
  config.py
  manage.py
```

其中

- forms(表单): 存放表单对象
- models(模型): 存放数据模型，即库表在程序中的映射对象，以及对象之间的关系
- routes(路由): 存放请求路由以及处理逻辑
- static(静态文件): [flask](https://xugaoxiang.com/tag/flask/)约定存放静态文件的目录
- templates(模板): [flask](https://xugaoxiang.com/tag/flask/)约定存放页面模板的目录
- services(服务): 存放业务逻辑或者其他服务类功能
- **init**.py: [flask](https://xugaoxiang.com/tag/flask/) app初始化方法
- config.py: 项目配置文件
- manage.py: 启动一个开发服务器，但是不会在生产环境中用到

### 备注

说到`flask`项目结构，绝对离不开蓝图，即`blueprint`，这部分内容，放在下一篇中分享