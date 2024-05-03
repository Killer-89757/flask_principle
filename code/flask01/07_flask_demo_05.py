from flask import Flask,render_template,request,redirect,session,url_for

app = Flask(__name__)
app.secret_key = "1233467890rtyuiopvbnm"

@app.route("/login",methods=['GET',"POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    user = request.form.get("user")
    pwd = request.form.get("pwd")
    print(user,pwd)
    if user == "waws" and pwd == "123456":
        session['xxx'] = 'waws'
        return redirect("/index")
    error_msg = "用户名或者密码错误"
    return render_template("login.html",error=error_msg)


@app.route("/index")
def index():
    username = session.get('xxx')
    if not username:
        return redirect(url_for('login'))
    return "首页"

if __name__ == '__main__':
    app.run()