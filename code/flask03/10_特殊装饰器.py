from flask import Flask,render_template,request

app = Flask(__name__)

@app.before_request
def f1():
    print('f1')
    # return '123'

@app.before_request
def f2():
    print('f2')

@app.after_request
def f10(response):
    print('f10')
    return response

@app.after_request
def f20(response):
    print('f20')
    return response

@app.route('/index')
def index():
    print('index')
    return render_template('index.html')

if __name__ == '__main__':
    app.run()
    app.__call__