from flask import Flask

app = Flask(__name__,static_url_path='/xx')

# app.config =  Config对象
# Config对象.from_object('xx.xx')
# app.config
# app.config.from_object('xx.xx')

@app.before_request
def f1():
    pass

@app.after_request
def f2(response):
    return response

@app.before_first_request
def f3():
    pass


@app.route('/index')
def index():
    return 'hello world'

if __name__ == '__main__':
    app.run()
    app.__call__