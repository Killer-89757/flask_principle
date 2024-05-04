from flask import Flask,render_template

app = Flask(__name__)

# 加载配置文件
app.config.from_object('config.settings')

print(app.config['DB_HOST'])

@app.route('/index')
def index():
    return 'index'

if __name__ == '__main__':
    app.run()