from flask import Flask,render_template,request,redirect

app = Flask(__name__)

@app.route("/login",methods=['GET',"POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    user = request.form.get("user")
    pwd = request.form.get("pwd")
    if user == "waws" and pwd == "123456":
        return redirect("/index")
    error_msg = "用户名或者密码错误"
    return render_template("login.html",error=error_msg)


@app.route("/index")
def index():
    return "首页"

if __name__ == '__main__':
    app.run()