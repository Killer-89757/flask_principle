from flask import Flask, session, request, current_app, g
# 1.1
app = Flask(__name__,static_url_path='/xx')

@app.route('/index')
def index():
    # session, request, current_app, g 全部都是LocalProxy对象。
    """
    session['x'] = 123     ctx.session['x'] = 123
    request.method         ctx.request.method
     current_app.config    app_ctx.app.config
     g.x1                  app_ctx.g.x1
    """
    session['k1'] = 123
    print(request.args)
    print(request.form)

    return 'hello world'

if __name__ == '__main__':
    app.run()