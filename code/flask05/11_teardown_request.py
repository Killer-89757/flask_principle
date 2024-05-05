from flask import Flask,render_template,g
from flask import signals
app = Flask(__name__)

@app.teardown_request
def f12(exc):
    print('teardown_request f12 被触发')

@app.route('/index/')
def index():
    return render_template('index.html')

@app.route('/order')
def order():
    print('order')
    return render_template('order.html')

if __name__ == '__main__':
    app.run()