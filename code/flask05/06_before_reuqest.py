from flask import Flask,render_template,g
from flask import signals
app = Flask(__name__)

@app.before_request
def f6():
    g.xx = 123
    print('before_request被触发')

@app.route('/index')
def index():
    print('index')
    return "index"

@app.route('/order')
def order():
    print('order')
    return "order"

if __name__ == '__main__':
    app.run()