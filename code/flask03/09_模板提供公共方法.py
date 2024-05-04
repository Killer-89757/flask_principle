from flask import Flask,render_template

app = Flask(__name__,)

@app.template_global() #  {{ func("赵海宇") }}
def func(arg):
    return '海狗子' + arg

@app.template_filter() # {{ "赵海宇"|x1("孙宇") }}
def x1(arg,name):
    return '海狗子' + arg + name


@app.route('/md/hg')
def index():
    return render_template('md_hg.html')

if __name__ == '__main__':
    app.run()