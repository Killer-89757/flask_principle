# Flask教程(十一)数据库操作flask_sqlalchemy

### 软硬件环境

- windows 10 64bit
- anaconda3 with [python](https://xugaoxiang.com/tag/python/) 3.7
- pycharm 2020.1.2
- [flask](https://xugaoxiang.com/tag/flask/) 1.1.2
- [sqlite](https://xugaoxiang.com/tag/sqlite/)3

### 前言

在`web`开发中，离不开数据库操作。前文我们已经介绍过`SQLAlchemy`这个`ORM`, [python使用sqlalchemy操作mysql数据库](https://xugaoxiang.com/2020/06/16/python-sqlalchemy-mysql/), 真的非常简单好用。`Flask-SQLAlchemy`是`flask`的扩展，它将`SQLAlchemy`的支持带到了`flask`应用程序中

### 安装

使用老方法安装

```
pip install flask_sqlalchemy
```

### [sqlite](https://xugaoxiang.com/tag/sqlite/)安装

```mysql
SQLAlchemy`操作`mysql`的示例前面已经演示过了，这次我们使用`sqlite`数据库。`sqlite`是一款轻量级的数据库，可以很方便的在嵌入式设备或者移动设备上使用，支持主流的操作系统`win`、`linux`、`macOS`、`android`等，目前版本已经发展到了`sqlite3
```

来到官方站点 https://www.sqlite.org/download.html，根据自己的平台进行选择下载

![flask-sqlalchemy](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fe5b026f717a1e8ef-18a197.png)

将下载下来的2个压缩包分别加压缩，然后将里面的文全部件放在一个文件夹里，方便使用，然后将这个文件夹的路径加入到系统的环境变量里

![flask-sqlalchemy](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F54e85b8e3986a781-1bea23.png)

![flask-sqlalchemy](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F8e428dab159ca513-63f221.png)

然后，我们在任意位置，打开终端，就都可以直接使用`sqlite.exe`了

![flask-sqlalchemy](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F64cc08d83b0a63be-4cacaf.png)

如果不熟悉`sql`的命令的话，可以使用图形化客户端，这里推荐一个工具，它是一个开源的项目，可以下面的地址进行下载

https://sqlitebrowser.org/dl/

### 代码示例

这里还是使用上一节 [Flask教程(十)表单处理Flask-WTF](https://xugaoxiang.com/2020/07/09/flask-10-wtf/) 中的用户注册是示例，在原来的基础上进行修改，当用户提交注册信息的时候，`flask`会去数据库中进行查询，如果用户名不存在则将用户信息写入`sqlite`，否则给出无效用户名的错误信息，要求用户重新填写

```python
from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Length, Email
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "xxx"
# 设置数据库URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///member.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


# 使用app作为参数实例化一个SQLAlchemy类的对象
db = SQLAlchemy(app)

# 创建会员模型
class Member(db.Model):
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(45), unique=True)
    email = db.Column(db.String(45))
    password = db.Column(db.String(128))

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

# 创建数据表
db.create_all()

# 使用WTF实现表单，自定义一个表单类
class RegisterForm(FlaskForm):
    username = StringField(label='用户名: ', validators=[DataRequired()])
    email = StringField(label='邮箱: ', validators=[DataRequired(), Email(message='邮箱格式错误')])
    password = PasswordField(label='密码: ', validators=[DataRequired(), Length(6, 16, message='密码格式错误')])
    password2 = PasswordField(label='确认密码: ', validators=[DataRequired(), Length(6, 16, message='密码格式错误'), EqualTo('password', message='密码不一致')])
    submit = SubmitField(label='注册')


@app.route('/', methods=['GEt', 'POST'])
def register():
    register_form = RegisterForm()

    if request.method == 'POST':
        if register_form.validate_on_submit():
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')

            # 判断数据库中是否已经存在相同的用户名
            if Member.query.filter_by(username=username).all():
                return 'Invalid username'

            # 构建数据库记录并写入数据库
            member = Member(username=username, email=email, password=password)
            db.session.add(member)
            db.session.commit()
            return 'Register success.'

        else:
            return 'Invalid'

    # 把实例化后的register_form传入到页面register.html中
    return render_template('register.html', form=register_form)


if __name__ == '__main__':
    app.run(host="127.0.0.1",port=5000,debug=True)
```

模板文件跟原来的一样，只有一个`form`表单，没有做任何修改

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Register</title>
</head>
<body>

    <form method="post">
        {{ form.csrf_token() }}
        {{ form.username.label }} {{ form.username }} <br>
        {{ form.email.label }} {{ form.email  }} <br>
        {{ form.password.label }} {{ form.password }} <br>
        {{ form.password2.label }} {{ form.password2 }} <br>
        {{ form.submit }}
    </form>

</body>
</html>
```

程序运行起来后，访问`http://127.0.0.1:5000`，输入满足条件的注册信息

![flask-sqlalchemy](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F6b089ae9698bb29e-6e0464.png)

![flask-sqlalchemy](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F4c0b742f4266f95f-a64d31.png)

在项目根目录生成了数据库文件`member.sqlite3`

![flask-sqlalchemy](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fae57b1fb7feb11dd-14b751.png)

使用图形化工具`DB Browser`打开`member.sqlite3`可以看到刚才注册成功的用户信息，利用工具，可以很方便的进行数据的增删改查

![flask-sqlalchemy](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fc459a67b7b6cb9f3-c2dc15.png)

如果用户名已经被注册过了，则页面提示错误信息，相应的信息也不会被写入数据库

![flask-sqlalchemy](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F298f3cc169e78604-b65c8e.png)

### 备注

如果出现警告

```
UserWarning SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead
```

可以通过设置`app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True`来消除上面的警告