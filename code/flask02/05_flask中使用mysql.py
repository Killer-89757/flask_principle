from flask import Flask
import sqlhelper as sqlhelper

app = Flask(__name__)

@app.route('/login')
def login():
    result = sqlhelper.fetchone('select * from silimar_cat where name=%s ','金吉拉猫')
    print(result)
    return 'login'


@app.route('/index')
def index():
    result = sqlhelper.fetchall('select * from silimar_cat')
    print(result)
    return 'xxx'


@app.route('/order')
def order():
    # result = fetchall('select * from user')
    return 'xxx'


if __name__ == '__main__':
    app.run()