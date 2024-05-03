from flask import Flask,render_template,request,redirect,url_for

app = Flask(__name__)

data_dict = {
    "1":{"name":"狗剩",'age':18,"gender":"男"},
    "2":{"name":"钢蛋",'age':20,"gender":"女"},
    "3":{"name":"铁锤",'age':40}
}

@app.route("/index",endpoint='idx')
def index():
    return render_template("index.html",data_dict=data_dict)

@app.route("/edit",methods=["GET","POST"])
def edit():
    # 拿到的都是字符串类型
    nid = request.args.get("nid")

    if request.method =="GET":
        info = data_dict[nid]
        return render_template("edit.html",info=info)
    user = request.form.get('name')
    age = int(request.form.get('age'))
    gender = request.form.get("gender")
    data_dict[nid]["name"] = user
    data_dict[nid]["age"] = age
    data_dict[nid]["gender"] = gender
    return redirect(url_for("idx"))


@app.route("/del/<nid>")
def delete(nid):
    del data_dict[nid]
    print("删除成功")
    return redirect(url_for('idx'))

if __name__ == '__main__':
    app.run()