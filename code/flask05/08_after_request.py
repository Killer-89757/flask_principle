from flask import Flask,render_template,g
from flask import signals
app = Flask(__name__)

@app.after_request
def f9(response):
    print('after_request f9 被触发')
    return response

@app.route('/index/')
def index():
    return render_template('index.html')

@app.route('/order')
def order():
    print('order')
    return render_template('order.html')

if __name__ == '__main__':
    app.run()