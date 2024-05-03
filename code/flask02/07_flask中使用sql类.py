from flask import Flask
# 这个就是单例模式的调用
from sqlhelper2 import db

app = Flask(__name__)

@app.route('/login')
def login():
    print(db)
    # db.fetchone()
    return 'login'


@app.route('/index')
def index():
    print(db)
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