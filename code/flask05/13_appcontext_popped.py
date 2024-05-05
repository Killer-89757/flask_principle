from flask import Flask,render_template,g
from flask import signals
app = Flask(__name__)

@signals.appcontext_popped.connect
def f14(app):
    print('appcontext_popped f14 被触发')

@app.route('/index/')
def index():
    return render_template('index.html')

@app.route('/order')
def order():
    print('order')
    return render_template('order.html')

if __name__ == '__main__':
    app.run()