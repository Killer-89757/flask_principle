from flask import Flask,render_template

app = Flask(__name__,)

def func(arg):
    return '你好' + arg

@app.route('/md')
def index():
    nums = [11,222,33]
    return render_template('md.html',nums=nums,f=func)

if __name__ == '__main__':
    app.run()