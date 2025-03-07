from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return "Hello, Flask!"


@app.route("/auth")
def r_auth():
    return "Hello, Flask!"


@app.route("/stage")
def r_list_stage():
    return "Hello, Flask!"

 
@app.route("/data")
def home():
    return "Hello, Flask!"


@app.route("/data/<data_id>")
def get_data_by_id(data_id):
    return "Hello, Flask!"


@app.route("/data/<data_id>/action")
def r_apply_action(data_id):
    return "Hello, Flask!"


@app.route("/action")
def list_actions(data_id):
    return "Hello, Flask!"


if __name__ == "__main__":
    app.run(debug=True)
