from flask import Flask,render_template,session
app = Flask(__name__)
app.secret_key = 'iuknsoiuwknlskjdf'

@app.route('/index/')
def index():
    session['k1'] = 123
    return render_template('index.html')

@app.route('/order')
def order():
    val = session['k1']
    del session['k1']
    print(val)
    return render_template('order.html')

if __name__ == '__main__':
    app.run()