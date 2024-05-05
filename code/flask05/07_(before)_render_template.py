from flask import Flask,render_template,g
from flask import signals
app = Flask(__name__)

@signals.before_render_template.connect
def f7(app, template, context):
    print('before_render_template f7 被触发')

@signals.template_rendered.connect
def f8(app, template, context):
    print('template_rendered f8 被触发')

@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/order')
def order():
    return render_template("order.html")

if __name__ == '__main__':
    app.run()