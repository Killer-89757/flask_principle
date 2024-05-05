from flask import Flask,render_template
from flask import signals
app = Flask(__name__)

@signals.request_started.connect
def f3(arg):
    print('request_started信号被触发',arg)

@app.route('/index')
def index():
    return "index"

@app.route('/order')
def order():
    return "order"

if __name__ == '__main__':
    app.run()