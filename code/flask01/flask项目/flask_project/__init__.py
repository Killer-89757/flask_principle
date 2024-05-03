from flask import Flask

def create_app():
    app = Flask(__name__)
    app.secret_key = "jdoasfajkfpafkadsf"

    @app.route('/index')
    def index():
        return 'index'

    # 注册蓝图
    from .views.killer import killer
    from .views.waws import waws
    app.register_blueprint(killer,url_prefix='/killer')
    app.register_blueprint(waws,url_prefix='/waws')

    return app