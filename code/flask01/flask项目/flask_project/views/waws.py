from flask import Blueprint

waws = Blueprint('waws',__name__)

@waws.route('/f3')
def f1():
    return 'waws-f3'

@waws.route('/f4')
def f2():
    return 'waws-f4'