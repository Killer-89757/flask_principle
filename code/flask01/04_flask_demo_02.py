from flask import Flask,jsonify

app = Flask(__name__)


@app.route("/")
def index():
    return jsonify({"code":1000,"data":"kets"})


if __name__ == '__main__':
    app.run()