from flask import Flask,render_template
from flask import signals

app = Flask(__name__)

@signals.appcontext_pushed.connect
def f1(arg):
    print('appcontext_pushed信号f1被触发',arg)

@signals.appcontext_pushed.connect
def f2(arg):
    print('appcontext_pushed信号f2被触发',arg)

@app.route('/index')
def index():
    return "index"

@app.route('/order')
def order():
    return 'order'

if __name__ == '__main__':
    app.run()