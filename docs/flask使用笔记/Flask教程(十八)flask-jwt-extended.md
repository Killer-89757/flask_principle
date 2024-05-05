# Flask教程(十八)flask-jwt-extended

### 软硬件环境

- windows 10 64bit
- anaconda3 with python 3.7
- pycharm 2020.1.2
- [flask](https://xugaoxiang.com/tag/flask/) 1.1.2
- [flask](https://xugaoxiang.com/tag/flask/)-[jwt](https://xugaoxiang.com/tag/jwt/)-extended 3.24.1

### 前言

**在`web`开发中，`Client`与`Server`的交互都是通过`HTTP`协议发送请求和接收响应，但是因为`HTTP`协议是无状态的(`stateless`)，也就是说`Client`和`Server`都不会记得先前的状态，`Client`每次发送`request`都会被视为是独立的，`Server`无法确定`Client`是否已经发送过认证请求。**

本文分享基于`Token`即**令牌**的认证。在`flask`中，使用的扩展是`flask-jwt-extended`。

### 什么是JWT

`JWT`的原名是`JSON Web Token`，它是一种协定，**就是把`JSON`结构的信息进行加密后变成`Token`传递给`Client`端**，然后客户端通过这个`Token`来与服务器进行交互。简单来说就是：**使用者在登录或是验证过身份后，后端会在返回请求中附上`JWT Token`，未来使用者发送`Request`时携带此`Token`，就表示通过验证，而沒有携带`JWT Token`的使用者就会被拒绝访问，需要重新登录或重新验证身份。**

### 安装扩展

`flask-jwt-extended`是`JWT`的一个实现，有了它，使得我们在开发基于`flask`框架的`web`应用时能够更加方便地实现基于`Token`的认证过程。首先需要安装扩展

```python
pip install flask-jwt-extended
```

### 完整代码示例

这次示例，我们会用上之前介绍`flask-sqlalchemy`、`flask-cors`、`flask-restful`等扩展，编写一个相对完整的前后端分离的`web`后端系统，它具备如下功能

- 可以实现用户登录
- 用户登录信息的数据库存储
- 基于`Token`的前后端交互、`RESTful API`
- 跨域访问

先来看看整个项目的文件目录结构

![flask-jwt-extended](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fbc9ed591fc66bdad-ae7fd2.png)

首先我们准备下数据库，使用的是开源数据库`mysql`，创建数据库`flask`

![flask-jwt-extended](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F34660da1ad27dc70-146ad0.png)

通过`scripts`目录下的`dbInitialize.py`脚本文件创建初始数据库表并插入一条数据，用户名是`admin@gmail.com`，密码是字符串`123456`经过`sha256`加密后的数据，默认用户是激活状态

`user`表的结构是这样的

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(45), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)

    def __init__(self, username=None, password=None, active=True):
        self.username = username
        self.password = password
        self.active = True
```

![flask-jwt-extended](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Ff78a09702b75c49b-a9e301.png)

重点来看看用户登录部分的后端实现，还是`RESTful API`，这里提供一个`POST`方法，接收客户端发送过来的`JSON`数据，解析后得到用户名及加密后的密码，如果用户名存在于我们的数据库中且密码相符，调用`flask_jwt_extended`的`create_access_token`方法生成对应的`token`，注意到`create_access_token`的参数部分，我们传递的是`username`。`flask_jwt_extended`还提供了方法`get_jwt_identity`，可以从`token`中获取到`username`，这点在实际项目中非常有用。

```python
class Login(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    def post(self):
        code = None
        message = None
        token = None
        userid = None

        args = reqparse.RequestParser() \
            .add_argument('username', type=str, location='json', required=True, help="用户名不能为空") \
            .add_argument("password", type=str, location='json', required=True, help="密码不能为空") \
            .parse_args()

        flag_user_exist, flag_password_correct, user = User.authenticate(args['username'], args['password'])
        if not flag_user_exist:
            code = 201
            message = "user not exist"
        elif not flag_password_correct:
            code = 202
            message = "wrong password"
        else:
            code = 200
            message = "success"
            token = create_access_token(identity=user.username)
            userid = user.id

        return jsonify({
            "code": code,
            "message": message,
            "token": token,
            "userid": userid
        })
```

我们通过`postman`来模拟客户端的行为

![flask-jwt-extended](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F14c267a876f89eab-02c743.png)

可以看到，`postman`拿到了服务器发送过来的`token`值，保存这个值，后面的所有接口都需要带上这个`token`。接下来看看获取所有用户信息的接口

```python
class Users(Resource):
    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

    @jwt_required
    def get(self):
        users_list = []
        users = User.get_users()

        for user in users:
            users_list.append({"userid": user.id, "username": user.username})

        return jsonify({
            "code": 200,
            "message": "success",
            "users": users_list
        })
```

注意到上面的`get`方法有个装饰器`@jwt_required`，意思就是说这个接口是需要验证`token`的，所以，客户端在调用这个接口的时候就需要带上`token`，否则会报`Missing Authorization Header`的错误

![flask-jwt-extended](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F6f596c98737506b2-3dafe0.png)

正确的做法是这样的，在`Headers`添加字段

```
"Authorization: Bearer $ACCESS_TOKEN"
```

这里面的`Bearer`是`token`的一种类型，还有另一个类型是`Mac Token`，这是固定写法

![flask-jwt-extended](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2F31902a8cbdb1087a-ee067b.png)

### 定制Token过期的返回信息

```python
flask-jwt-extended`在`token`过期后，有自己默认的出错信息，如果不满意，可以自己定制出错信息，使用装饰器`@jwt.expired_token_loader
@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({
        'code': 201,
        'message': "token expired"
    })
```

### Signature has expired处理

在程序运行时，无意中出现了`Signature has expired`的异常

```python
File "/usr/local/lib/python3.5/site-packages/flask/app.py", line 1639, in full_dispatch_request
rv = self.dispatch_request()
File "/usr/local/lib/python3.5/site-packages/flask/app.py", line 1625, in dispatch_request
return self.view_functions[rule.endpoint](**req.view_args)
File "/usr/local/lib/python3.5/site-packages/flask_restful/__init__.py", line 477, in wrapper
resp = resource(*args, **kwargs)
File "/usr/local/lib/python3.5/site-packages/flask/views.py", line 84, in view
return self.dispatch_request(*args, **kwargs)
File "/usr/local/lib/python3.5/site-packages/flask_restful/__init__.py", line 587, in dispatch_request
resp = meth(*args, **kwargs)
File "/usr/local/lib/python3.5/site-packages/flask_jwt_extended/utils.py", line 222, in wrapper
jwt_data = _decode_jwt_from_request(type='access')
File "/usr/local/lib/python3.5/site-packages/flask_jwt_extended/utils.py", line 204, in _decode_jwt_from_request
return _decode_jwt_from_headers()
File "/usr/local/lib/python3.5/site-packages/flask_jwt_extended/utils.py", line 176, in _decode_jwt_from_headers
return _decode_jwt(token, secret, algorithm)
File "/usr/local/lib/python3.5/site-packages/flask_jwt_extended/utils.py", line 136, in _decode_jwt
data = jwt.decode(token, secret, algorithm=algorithm)
File "/usr/local/lib/python3.5/site-packages/jwt/api_jwt.py", line 75, in decode
self._validate_claims(payload, merged_options, **kwargs)
File "/usr/local/lib/python3.5/site-packages/jwt/api_jwt.py", line 104, in _validate_claims
self._validate_exp(payload, now, leeway)
File "/usr/local/lib/python3.5/site-packages/jwt/api_jwt.py", line 149, in _validate_exp
raise ExpiredSignatureError('Signature has expired')
jwt.exceptions.ExpiredSignatureError: Signature has expired
```

`google`一番，看到官方的`issue`里有讨论这个问题，结论是在`flask-jwt-extended`配置中添加`PROPAGATE_EXCEPTIONS = True`，有兴趣的话，请查看参考资料里的链接。关于工程的所有配置信息，便于统一管理，我们集中在`app/config.py`中书写

```python
import os


class Config:
    # flask
    DEBUG = os.environ.get('FLASK_DEBUG') or True

    # database
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'mysql+pymysql://root:toor@localhost/test'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # jwt
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-key'
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_CSRF_CHECK_FORM = True
    JWT_ACCESS_TOKEN_EXPIRES = os.environ.get('JWT_ACCESS_TOKEN_EXPIRES') or 3600
    PROPAGATE_EXCEPTIONS = True
```

在生产环境中，可以通过对应的环境变量来获取配置，能够比较方便地区分调试和生产环境