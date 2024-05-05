from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.settings')

    from .views.account import ac
    from .views.car import car

    app.register_blueprint(ac)
    app.register_blueprint(car)

    return app