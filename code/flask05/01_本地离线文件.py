from flask import current_app, g, Flask


def create_app():
    app = Flask(__name__)

    @app.route('/index')
    def index():
        return 'index'

    return app


app1 = create_app()
with app1.app_context():  # AppContext对象(app,g) -> local对象
    print(current_app.config)  # -1 top app1
    app2 = create_app()
    with app2.app_context():  # AppContext对象(app,g) -> local对象
        print(current_app.config)  # top -1 app2
    print(current_app.config)  # top -1 app1

if __name__ == '__main__':
    app1.run()