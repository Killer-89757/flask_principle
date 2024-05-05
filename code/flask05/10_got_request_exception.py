from flask import Flask,render_template,g
from flask import signals
app = Flask(__name__)

@app.before_first_request
def test():
    int('asdf')

@signals.got_request_exception.connect
def f11(app,exception):
    print('got_request_exception f11 被触发')

@app.route('/index/')
def index():
    return render_template('index.html')

@app.route('/order')
def order():
    print('order')
    return render_template('order.html')

if __name__ == '__main__':
    app.run()