from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

gramatas = []

@app.route("/")
def sakums ():
    return render_template("lpp1.html")

@app.route("/saraksts")
def saraksts():
    return render_template("lpp2saraksts.html", gramatas=gramatas)

@app.route("/pievienot", methods=["GET", "POST"])
def pievienot():
    if request.method == "POST":
        nosaukums = request.form["nosaukums"]
        gads = request.form["gads"]
        autors = request.form["autors"]
        zanrs = request.form["zanrs"]
        isuma = request.form["isuma"]
        statuss = request.form.get("statuss", "Nav norādīts")

        gramata = {
            "nosaukums": nosaukums,
            "gads": gads,
            "autors": autors,
            "zanrs": zanrs,
            "isuma": isuma,
            "statuss": statuss
        }

        gramatas.append(gramata)  

        return redirect(url_for('saraksts'))

    return render_template("lpp3form.html")

if __name__ == "__main__":
    app.run(debug=True)