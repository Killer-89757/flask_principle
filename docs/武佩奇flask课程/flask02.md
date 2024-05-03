# flask02

## 今日概要

- 数据库连接池
- 上下文管理机制

## 今日详细

### 1.数据库连接池

#### 1.1 初级阶段

```python
import pymysql
from flask import Flask

app = Flask(__name__)


def fetchall(sql):
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123', db='t1')
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

@app.route('/login')
def login():
    result = fetchall('select * from user')
    return 'login'


@app.route('/index')
def index():
    result = fetchall('select * from user')
    return 'xxx'


@app.route('/order')
def order():
    result = fetchall('select * from user')
    return 'xxx'


if __name__ == '__main__':
    app.run()
```

#### 1.2 老板给修改

```python
import pymysql
from flask import Flask

app = Flask(__name__)

CONN = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123', db='t1')

def fetchall(sql):
    cursor = CONN.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    return result

@app.route('/login')
def login():
    result = fetchall('select * from user')
    return 'login'


@app.route('/index')
def index():
    result = fetchall('select * from user')
    return 'xxx'


@app.route('/order')
def order():
    result = fetchall('select * from user')
    return 'xxx'


if __name__ == '__main__':
    app.run()
```

#### 2.3 数据库连接池

安装

```
pip3 install dbutils
pip3 install pymysql
```

使用

```python
import pymysql
# from DBUtils.PooledDB import PooledDB
from dbutils.pooled_db import PooledDB

POOL = PooledDB(
    creator=pymysql,  # 使用链接数据库的模块
    maxconnections=6,  # 连接池允许的最大连接数，0和None表示不限制连接数
    mincached=2,  # 初始化时，链接池中至少创建的链接，0表示不创建
    blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
    ping=0, # ping MySQL服务端，检查是否服务可用。# 如：0 = None = never, 1 = default = whenever it is requested, 2 = when a cursor is created, 4 = when a query is executed, 7 = always

    host='127.0.0.1',
    port=3306,
    user='root',
    password='222',
    database='cmdb',
    charset='utf8'
)

# 去连接池中获取一个连接
conn = POOL.connection()

cursor = conn.cursor()
cursor.execute('select * from web_models_disk')
result = cursor.fetchall()
cursor.close()

# 将连接放会到连接池
conn.close()

print(result)
```

多线程测试

```python
import pymysql
# from DBUtils.PooledDB import PooledDB
from dbutils.pooled_db import PooledDB

POOL = PooledDB(
    creator=pymysql,  # 使用链接数据库的模块
    maxconnections=6,  # 连接池允许的最大连接数，0和None表示不限制连接数
    mincached=2,  # 初始化时，链接池中至少创建的链接，0表示不创建
    blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
    ping=0, # ping MySQL服务端，检查是否服务可用。# 如：0 = None = never, 1 = default = whenever it is requested, 2 = when a cursor is created, 4 = when a query is executed, 7 = always

    host='127.0.0.1',
    port=3306,
    user='root',
    password='222',
    database='cmdb',
    charset='utf8'
)


def task(num):
    # 去连接池中获取一个连接
    conn = POOL.connection()
    cursor = conn.cursor()
    # cursor.execute('select * from web_models_disk')
    cursor.execute('select sleep(3)')
    result = cursor.fetchall()
    cursor.close()
    # 将连接放会到连接池
    conn.close()
    print(num,'------------>',result)


from threading import Thread
for i in range(57):
    t = Thread(target=task,args=(i,))
    t.start()
```

##### 基于函数实现sqlhelper

```python
import pymysql
# from DBUtils.PooledDB import PooledDB
from dbutils.pooled_db import PooledDB

POOL = PooledDB(
    creator=pymysql,  # 使用链接数据库的模块
    maxconnections=6,  # 连接池允许的最大连接数，0和None表示不限制连接数
    mincached=2,  # 初始化时，链接池中至少创建的链接，0表示不创建
    blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
    ping=0, # ping MySQL服务端，检查是否服务可用。# 如：0 = None = never, 1 = default = whenever it is requested, 2 = when a cursor is created, 4 = when a query is executed, 7 = always

    host='127.0.0.1',
    port=3306,
    user='root',
    password='222',
    database='cmdb',
    charset='utf8'
)

def fetchall(sql,*args):
    """ 获取所有数据 """
    conn = POOL.connection()
    cursor = conn.cursor()
    cursor.execute(sql,args)
    result = cursor.fetchall()
    cursor.close()
    conn.close()

    return result

def fetchone(sql, *args):
    """ 获取单挑数据 """
    conn = POOL.connection()
    cursor = conn.cursor()
    cursor.execute(sql, args)
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    return result
```

```python
from flask import Flask
import sqlhelper

app = Flask(__name__)

@app.route('/login')
def login():
    result = sqlhelper.fetchone('select * from web_models_admininfo where username=%s ','wupeiqi')
    print(result)
    return 'login'


@app.route('/index')
def index():
    result = sqlhelper.fetchall('select * from web_models_disk')
    print(result)
    return 'xxx'


@app.route('/order')
def order():
    # result = fetchall('select * from user')
    return 'xxx'


if __name__ == '__main__':
    app.run()
```

##### 基于类实现sqlhelper

```python
import pymysql
from dbutils.pooled_db import PooledDB

class SqlHelper(object):
    def __init__(self):
        self.pool = PooledDB(
            creator=pymysql,  # 使用链接数据库的模块
            maxconnections=6,  # 连接池允许的最大连接数，0和None表示不限制连接数
            mincached=2,  # 初始化时，链接池中至少创建的链接，0表示不创建
            blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
            ping=0,
            # ping MySQL服务端，检查是否服务可用。# 如：0 = None = never, 1 = default = whenever it is requested, 2 = when a cursor is created, 4 = when a query is executed, 7 = always
            host='127.0.0.1',
            port=3306,
            user='root',
            password='111111',
            database='cat_12',
            charset='utf8'
        )

    def open(self):
        conn = self.pool.connection()
        cursor = conn.cursor()
        return conn,cursor

    def close(self,cursor,conn):
        cursor.close()
        conn.close()

    def fetchall(self,sql, *args):
        """ 获取所有数据 """
        conn,cursor = self.open()
        cursor.execute(sql, args)
        result = cursor.fetchall()
        self.close(conn,cursor)
        return result

    def fetchone(self,sql, *args):
        """ 获取所有数据 """
        conn, cursor = self.open()
        cursor.execute(sql, args)
        result = cursor.fetchone()
        self.close(conn, cursor)
        return result

# 在这里生成一个对象，外表调用自然是单例模式
db = SqlHelper()
```

```python
from flask import Flask
from sqlhelper2 import db

app = Flask(__name__)

@app.route('/login')
def login():
    # db.fetchone()
    return 'login'


@app.route('/index')
def index():
    # db.fetchall()
    return 'xxx'

@app.route('/order')
def order():
    # db.fetchall()
    conn,cursor = db.open()
    # 自己做操作
    db.close(conn,cursor)
    return 'xxx'

if __name__ == '__main__':
    app.run()
```

![image-20240503230644951](https://cdn.jsdelivr.net/gh/Killer-89757/PicBed/images/2024%2F05%2Fimage-20240503230644951-20be8f.png)

### 2.补充知识点：上下文管理

```python
class Foo(object):

    def __enter__(self):
        return 123

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

obj = Foo()

with obj as f:
    print(f)
```

```python
class Foo(object):

    def do_somthing(self):
        print("do something")

    def close(self):
        print("close")


# 使用context去管理Foo类的执行和关闭
class Context:
    def __enter__(self):
        self.data = Foo()
        return self.data

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.data.close()


with Context() as ctx:
    ctx.do_somthing()
```
