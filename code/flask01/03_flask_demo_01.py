from flask import Flask,render_template

app = Flask(__name__)


@app.route("/login")
def index():
    return render_template("login.html")


if __name__ == '__main__':
    app.run()