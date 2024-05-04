import pymysql
from dbutils.pooled_db import PooledDB

POOL = PooledDB(
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


class SqlHelper(object):
    def __init__(self):
        self.conn = None
        self.cursor = None

    def open(self):
        conn = POOL.connection()
        cursor = conn.cursor()
        return conn, cursor

    def close(self):
        self.cursor.close()
        self.conn.close()

    def __enter__(self):
        self.conn, self.cursor = self.open()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# ################## 使用 ##################

with SqlHelper() as c1:
    c1.execute('select 1')
    with SqlHelper() as c2:
        c2.execute('select 2')
    print(666)

with SqlHelper() as cursor:
    cursor.execute('select 1')

with SqlHelper() as cursor:
    cursor.execute('select 1')
