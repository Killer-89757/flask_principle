from flask import Blueprint,render_template

car = Blueprint('car',__name__)

# 浏览器默认在index会自动补全，127.0.0.1:5000/index/ 导致我们的路由匹配出现异常
# 使用strict_slashes可以匹配成功
@car.route('/index',strict_slashes=False)
def index():
    return render_template('car/index.html')


@car.route('/add')
def add():
    return render_template('car/add.html')