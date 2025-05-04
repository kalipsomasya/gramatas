from flask import Flask, render_template, request, redirect, url_for 
import sqlite3
import os  #vajag lai izveidot ceļu datubazei

#atsevisks ceļš datu bazei, jo man bija kaut kāda kļūda ar dubult faila izveidi un prasiju čatam gpt ka atrisinat
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  #iegust ceļu uz mapi
DB_PATH = os.path.join(BASE_DIR, "gramatas.db")    #taisa ceļu uz datu bāzi


app = Flask(__name__)

#sakumlapa ar statistikas lodziņiem
@app.route("/")
def sakums ():
    conn = sqlite3.connect(DB_PATH)  #visur kur vajadzētu norādīt datubāzi norādu mainīgu ar ceļu uz to
    cur = conn.cursor()
    
    # saskaita kopējo grāmatu skaitu
    cur.execute("SELECT COUNT(*) FROM gramatas")
    total = cur.fetchone()[0]

    #saskaita grāmatas ar statusu izlasīts
    cur.execute("SELECT COUNT(*) FROM gramatas WHERE statuss = 'Izlasīts'")
    read = cur.fetchone()[0]

    #saskaita grāmatas ar statusu plānā
    cur.execute("SELECT COUNT(*) FROM gramatas WHERE statuss = 'Plānā'")
    planned = cur.fetchone()[0]

    conn.close()
    #atgriež 1. html lapu ar statistikas datiem
    return render_template("lpp1.html", total=total, read=read, planned=planned)

#grāmatu saraksta lapa ar kārtošanu
@app.route("/saraksts")
def saraksts():
    #iegust kartošanas parametrus
    sort_by = request.args.get("sort", default="id")
    order = request.args.get("order", default="asc")
    zanrs = request.args.get("zanrs")
    gads_range = request.args.get("gads")
    statuss = request.args.get("statuss")

    #sql
    query = "SELECT * FROM gramatas WHERE 1=1"
    params = []

    #pielieto filtru pec žanra ja izvēlas
    if zanrs:
        query += " AND zanrs = ?"
        params.append(zanrs)

    #ja izvēlēts gadu diapazons, pievieno filtrēšanu pēc gadiem (piemēram, 2000–2004)
    if gads_range:
        start = int(gads_range)
        end = start + 4
        query += " AND gads BETWEEN ? AND ?"
        params += [str(start), str(end)]
    #filtrs pēc gramatas statusa
    if statuss:
        query += " AND statuss = ?"
        params.append(statuss)

    #iestata virzienu katrošanai
    valid_sorts = ["nosaukums", "autors", "zanrs", "gads", "statuss"]
    if sort_by not in valid_sorts:
        sort_by = "id"
    if order not in ["asc", "desc"]:  #pā un pret numerāciju/alfabetu
        order = "asc"

    query += f" ORDER BY {sort_by} {order}"

    #pieslēdzas db un iegūst datus
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  #piekļuve pie kolonnas nosaukuma
    cur = conn.cursor()

    cur.execute(query, params)  #vaicajums ar nosacijumiem
    gramatas = cur.fetchall()  #iegūst grāmatas

    #iegūst visus unikālus žanrus kurus lietotajs pierakstījs
    cur.execute("SELECT DISTINCT zanrs FROM gramatas")
    visi_zanri = [row[0] for row in cur.fetchall()]

    #iegust visus pierakstītus gadus, noniem nepareizus un grupē pa pieciem gadiem(chat gpt)
    cur.execute("SELECT DISTINCT gads FROM gramatas ORDER BY gads ASC")
    gadi = sorted(set(int(r[0]) for r in cur.fetchall() if r[0].isdigit()))
    grupeti_gadi = sorted(set(gadi[i] - gadi[i] % 5 for i in range(len(gadi))))

    conn.close()

    #rāda 2. htnl lapu ar grāmatu sarakstu un filtriem
    return render_template("lpp2saraksts.html",
                           gramatas=gramatas,
                           visi_zanri=visi_zanri,
                           grupeti_gadi=grupeti_gadi,
                           active_filters={
                               "sort": sort_by,
                               "order": order,
                               "zanrs": zanrs,
                               "gads": gads_range,
                               "statuss": statuss
                           })


#formas lapa
@app.route("/pievienot", methods=["GET", "POST"])
def pievienot():
    if request.method == "POST":
        #iegūst datus no formas
        nosaukums = request.form["nosaukums"].title()
        gads = request.form["gads"]
        autors = request.form["autors"].title()
        zanrs = request.form["zanrs"].title()
        isuma = request.form["isuma"].capitalize()
        statuss = request.form.get("statuss")

        #ievieto jaunus datubāzē
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO gramatas (nosaukums, gads, autors, zanrs, isuma, statuss)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nosaukums, gads, autors, zanrs, isuma, statuss))
        conn.commit()
        conn.close()

        return redirect(url_for('saraksts'))   #pēc pievienošanas uzreiz pariet uz lapu ar sarakstu

    return render_template("lpp3form.html") #ja get tad atstāj

#grāmatas dzēšana pec id
@app.route("/dzest/<int:id>")
def dzest(id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM gramatas WHERE id = ?", (id,))  #dzēš ar konkrēto id
    conn.commit()
    conn.close()
    return redirect(url_for("saraksts"))  #pec dzēsanas atgrieš artpakaļ uz sarakstu

#grāmatas redigēsana
@app.route("/rediģēt/<int:id>", methods=["GET", "POST"])
def rediget(id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if request.method == "POST":
        #iegust datus no formas
        nosaukums = request.form["nosaukums"].title()
        gads = request.form["gads"]
        autors = request.form["autors"].title()
        zanrs = request.form["zanrs"].title()
        isuma = request.form["isuma"].capitalize()
        statuss = request.form.get("statuss")

        #atjauno grāmatas datus datubāzē (piemeram lietotajs lasija grāmatu un pabeidza. maina statusu uz izlasīts)
        cur.execute("""
            UPDATE gramatas
            SET nosaukums = ?, gads = ?, autors = ?, zanrs = ?, isuma = ?, statuss = ?
            WHERE id = ?
        """, (nosaukums, gads, autors, zanrs, isuma, statuss, id))
        conn.commit()
        conn.close()

        return redirect(url_for("saraksts"))
    
    #ja get ielade grāmatu datubāze un parāda redigēšanas formu
    cur.execute("SELECT * FROM gramatas WHERE id = ?", (id,))
    gr = cur.fetchone()
    conn.close()
    return render_template("rediget.html", gr=gr)

if __name__ == "__main__":  #startē ja palaists tieši
    app.run(debug=True)  #palaiž ar debug iespēju