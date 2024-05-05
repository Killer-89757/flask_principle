# Flask教程(一)搭建开发环境

### 软硬件环境

- Windows 10 64bit
- Anaconda3 with [python](https://xugaoxiang.com/tag/python/) 3.7
- PyCharm 2019.3
- Flask 1.1.1

### 前言

从本篇开始，我们将开始基于`python`的`web`开发系列教程，我们使用的是轻量级的`web`框架`Flask`。

### Flask是什么

`Flask`是一个用来构建基于`python`语言的`web`应用程序的轻量级`web`框架。`Flask`的作者是来自`Pocoo`(由一群热爱`python`的人组建)的`Armin Ronacher`。本来只是作者的一个愚人节玩笑，不过后来大受欢迎，进而成为一个正式的项目。

`Flask`也被称为`microframework`即微框架，因为它使用简单的核心，但是扩展性和兼容性都非常强。

### 安装python环境

这里我们使用`Anaconda`，关于`Anaconda`的介绍，可以参考之前的这篇博文[Anaconda使用](https://xugaoxiang.com/2019/12/08/anaconda/)

### 安装Flask

我们使用`pip`进行安装，命令是

```
pip install flask
```

![flask](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F3f0c29de356c09f1-ba49ab.png)

然后测试下，安装是否成功。在`python`中导入`flask`，如果没有报错的话，就说明安装成功了

![flask](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F0470dfb5f50e772e-d68460.png)

### PyCharm中的配置

在系列教程中，我们会使用`PyCharm`这个集成开发环境，因此先进行简单的配置。首先创建一个工程`FlaskTutorial`，解释器就选择`Anaconda`，如下图所示

![flask](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fa9c422220dc199b0-fcbc46.png)