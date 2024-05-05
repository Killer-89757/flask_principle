from flask import Flask,render_template

app = Flask(__name__)

@app.before_first_request
def f2():
    print('before_first_requestf2被触发')

@app.route('/index')
def index():
    return "index"

@app.route('/order')
def order():
    return "order"

if __name__ == '__main__':
    app.run()