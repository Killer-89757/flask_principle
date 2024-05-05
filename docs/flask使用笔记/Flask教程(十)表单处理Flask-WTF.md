# Flask教程(十)表单处理Flask-WTF

### 软硬件环境

- windows 10 64bit
- anaconda3 with [python](https://xugaoxiang.com/tag/python/) 3.7
- pycharm 2020.1.2
- [flask](https://xugaoxiang.com/tag/flask/) 1.1.2
- flask_wtf 0.14.3

### 简介

`web`表单是`web`应用程序的基本功能。它是`HTML`页面中负责数据采集的部件。表单有三个部分组成：表单标签、表单域和表单按钮。前面的教程中提到过的用户登录和文件上传的实例中都有表单的身影。

### Flask-WTF

`Flask-WTF`是一个`Flask`扩展，它封装了`WTForms`。它的优势可以归纳为以下3点

- 可以快速定义表单模板
- 验证表单数据
- 能够保护所有表单免受跨站请求伪造(`CSRF`)的攻击

`WTForms`支持`HTML`字段有

|        字段         |                    说明                    |
| :-----------------: | :----------------------------------------: |
|     StringField     | 文本字段， 相当于type类型为text的input标签 |
|    TextAreaField    |                多行文本字段                |
|    PasswordField    |                密码文本字段                |
|     HiddenField     |                隐藏文本字段                |
|      DateField      |      文本字段， 值为datetime.date格式      |
|    DateTimeField    |    文本字段， 值为datetime.datetime格式    |
|    IntegerField     |            文本字段， 值为整数             |
|    DecimalField     |       文本字段， 值为decimal.Decimal       |
|     FloatField      |           文本字段， 值为浮点数            |
|    BooleanField     |         复选框， 值为True 和 False         |
|     RadioField      |                 一组单选框                 |
|     SelectField     |                  下拉列表                  |
| SelectMultipleField |          下拉列表， 可选择多个值           |
|      FileField      |                文件上传字段                |
|     SubmitField     |                表单提交按钮                |
|      FormFiled      |        把表单作为字段嵌入另一个表单        |
|      FieldList      |             子组指定类型的字段             |

`WTForms`支持的表单验证方法有

|   验证函数   |                          说明                           |
| :----------: | :-----------------------------------------------------: |
|    Email     |                   验证是电子邮件地址                    |
|   EqualTo    | 比较两个字段的值； 常用于要求输入两次密钥进行确认的情况 |
|  IPAddress   |                    验证IPv4网络地址                     |
|    Length    |                  验证输入字符串的长度                   |
| NumberRange  |                验证输入的值在数字范围内                 |
|   Optional   |               无输入值时跳过其它验证函数                |
| DataRequired |                    确保字段中有数据                     |
|    Regexp    |                使用正则表达式验证输入值                 |
|     URL      |                         验证url                         |
|    AnyOf     |                确保输入值在可选值列表中                 |
|    NoneOf    |                确保输入值不在可选列表中                 |

### 表单处理实例

在使用`Flask-WTF`之前，我们需要安装这个扩展，使用命令

```
pip install flask_wtf email_validator
```

另一个模块`email_validator`是为了示例代码中的邮箱验证准备的

接下来创建文件`run.py`

```python
from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Length, Email
app = Flask(__name__)
app.secret_key = "xxx"

# 使用WTF实现表单，自定义一个表单类
class RegisterForm(FlaskForm):
    username = StringField(label='用户名: ', validators=[DataRequired()])
    email = StringField(label='邮箱: ', validators=[DataRequired(), Email(message='邮箱格式错误')])
    password = PasswordField(label='密码: ', validators=[DataRequired(), Length(6, 16, message='密码格式错误')])
    password2 = PasswordField(label='确认密码: ', validators=[DataRequired(), Length(6, 16, message='密码格式错误'),
                                                         EqualTo('password', message='密码不一致')])
    submit = SubmitField(label='注册')

@app.route('/', methods=['GEt', 'POST'])
def login():
    register_form = RegisterForm()
    if request.method == 'POST':
        if register_form.validate_on_submit():
            这里默认会进行csrf验证
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            password2 = request.form.get('password2')
            if username == 'xgx' and password == password2 and email == 'test@gmail.com':
                # 进入这里就表示表单验证成功
                return 'Register success, username: {}, email: {}, password: {}'.format(username, email, password)
            else:
                return 'Error'
        else:
            return 'Invalid'
    # 把实例化后的register_form传入到页面register.html中
    return render_template('register.html', form=register_form)

if __name__ == '__main__':
    app.run(host="127.0.0.1",port=5000,debug=True)
```

在`templates`文件夹下新建`register.html`，文件内容为

```
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

启动项目后，访问`http://127.0.0.1:5000`，按照表单验证方法的要求填写，就可以完成注册

![img](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F9ad3c5d1fc96cf0c-594861.png)

![img](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F880394750295add3-769e64.png)

如果其中某项不满足要求，比如设置的密码位数小于6位，这里设置成3位，就会报错

![img](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fb44a667ed124af52-721e03.png)

![img](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Feb41da6316d5a717-8e0b50.png)