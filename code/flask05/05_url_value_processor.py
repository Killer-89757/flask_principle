from flask import Flask,render_template,g
from flask import signals
app = Flask(__name__)


@app.url_value_preprocessor
def f5(endpoint,args):
    print('f5')

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