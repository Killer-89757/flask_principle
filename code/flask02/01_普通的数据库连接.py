import pymysql
from flask import Flask

app = Flask(__name__)

CONN = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='111111', db='cat_12')
cursor = CONN.cursor()
sql = "select * from silimar"
cursor.execute(sql)
result = cursor.fetchall()
print(result)
cursor.close()

def fetchall(sql):
    cursor = CONN.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    return result

@app.route('/login')
def login():
    result = fetchall('select * from sil')
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