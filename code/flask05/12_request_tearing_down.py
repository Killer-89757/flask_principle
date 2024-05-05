from flask import Flask,render_template,g
from flask import signals
app = Flask(__name__)

@signals.request_tearing_down.connect
def f13(app,exc):
    print('request_tearing_down f13 被触发')

@app.route('/index/')
def index():
    return render_template('index.html')

@app.route('/order')
def order():
    print('order')
    return render_template('order.html')

if __name__ == '__main__':
    app.run()