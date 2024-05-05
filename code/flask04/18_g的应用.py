from flask import Flask,g

app = Flask(__name__,static_url_path='/xx')

@app.before_request
def f1():
    g.x1 = 123

@app.after_request
def f1(response):
    print(g.x1)
    return response

@app.route('/index')
def index():
    print(g.x1)
    return 'hello world'


if __name__ == '__main__':
    app.run()