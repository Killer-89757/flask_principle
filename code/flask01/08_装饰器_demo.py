from flask import Flask,render_template,request,session,redirect,url_for,jsonify
import functools

app = Flask(__name__)
app.secret_key = "013uherwengnkwdgnkwn"

def auth(func):
    @functools.wraps(func)
    def inner(*args,**kwargs):
        username = session.get('xxx')
        if not username:
            return redirect(url_for('login'))
        return func(*args,**kwargs)
    return inner


@app.route("/login",methods=['GET',"POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    user = request.form.get("user")
    pwd = request.form.get("pwd")
    if user == "waws" and pwd == "123456":
        session['xxx'] = 'waws'
        return redirect("/index")
    error_msg = "用户名或者密码错误"
    return render_template("login.html",error=error_msg)

@app.route("/edit")
@auth
def edit():
    return 'edit'

@app.route("/delete")
@auth
def delete():
    return "删除"

@app.route("/index")
def index():
    return "首页"


if __name__ == '__main__':
    app.run()