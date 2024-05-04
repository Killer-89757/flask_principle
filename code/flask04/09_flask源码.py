from flask import Flask

app = Flask(__name__,static_url_path='/xx')

# app.config =  Config对象
# Config对象.from_object('xx.xx')
# app.config
app.config.from_object('xx.xx')

@app.route('/index')
def index():
    return 'hello world'

if __name__ == '__main__':
    app.run()