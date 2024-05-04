from flask import Flask, render_template

app = Flask(__name__, )


@app.route('/index')
def index():
    return render_template('index.html')


@app.before_request
def func():
    print('xxx')


def x1():
    print('xxx')


app.before_request(x1)

if __name__ == '__main__':
    app.run()
