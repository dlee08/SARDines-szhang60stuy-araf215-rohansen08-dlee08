from flask import Flask, render_template
app = Flask(__name__)

key = open(".env").read().strip()

@app.route("/")
def hello():
    return render_template("map_temp.html", api_key=key)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
