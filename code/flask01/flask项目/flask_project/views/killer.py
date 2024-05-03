from flask import Blueprint

killer = Blueprint('killer',__name__)

@killer.route('/f1')
def f1():
    return 'killer-f1'

@killer.route('/f2')
def f2():
    return 'killer-f2'