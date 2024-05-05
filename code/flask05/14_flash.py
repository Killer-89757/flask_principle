from flask import Flask, render_template, flash, get_flashed_messages

app = Flask(__name__)
app.secret_key = 'iuknsoiuwknlskjdf'


@app.route('/index/')
def index():
    flash('123')
    return render_template('index.html')


@app.route('/order')
def order():
    messages = get_flashed_messages()
    print(messages)
    return render_template('order.html')


if __name__ == '__main__':
    app.run()
