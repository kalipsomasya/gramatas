from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def text ():
    return render_template("lpp1.html")

if __name__ == "__main__":
    app.run(debug=True)