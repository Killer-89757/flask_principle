from flask import Flask, render_template

app = Flask(__name__)

from werkzeug.routing import BaseConverter


class RegConverter(BaseConverter):
    def __init__(self, map, regex):
        super().__init__(map)
        self.regex = regex

    # 对匹配到的值进行处理的函数
    def to_python(self, value):
        # return value  默认匹配得到的是字符串
        return int(value)  # 将其变成数值型


app.url_map.converters['regex'] = RegConverter


@app.route('/index/<regex("\d+"):x1>')
def index(x1):
    print(x1, type(x1))     # 1 <class 'int'>
    return render_template('index.html')


if __name__ == '__main__':
    app.run()