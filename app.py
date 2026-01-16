from flask import Flask, render_template, request, redirect, url_for, flash, session
from urllib.parse import urlparse

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flash messages

users = {} 

from db import db, Benutzer, Produkt, Kategorie, Hauttyp, Bewertung

@app.route('/')
def index():
   # if 'user_email' not in session:
        #return redirect(url_for('login'))
    return render_template ('home.html')

@app.route('/login' , methods=['GET', 'POST'])
def login():
    # Wenn schon eingeloggt → direkt zur Hauptseite
    #if "user_email" in session:
        #return redirect(url_for("index"))

    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']

        # prüfen gegen users-Dict (statt test@example)
        if email in users and users[email]["password"] == password:
            session["user_email"] = email
            session["username"] = users[email]["username"]
            flash("Login successful!")
            return redirect(url_for('skin_type'))

        flash("Invalid credentials. Please try again.")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Wenn schon eingeloggt: nicht nochmal registrieren
    # if 'user_email' in session:
        #return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']

        # prüfen, ob Benutzer schon existiert
        if email in users:
            flash("User with this email already exists.")
            return redirect(url_for('register'))

        # neuen Nutzer speichern
        users[email] = {
            'username': username,
            'password': password
        }

        #  automatisch einloggen
        session['user_email'] = email
        session['username'] = username

        flash("Registration successful!")
        return redirect(url_for('skin_type'))  

    return render_template('register.html')
   
@app.route('/skin_type', methods=['GET', 'POST'])
def skin_type():
    # nur wenn eingeloggt
    if 'user_email' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        session['skin_type'] = request.form['skin_type']
        return redirect(url_for('products'))

    return render_template('skin_type.html')


@app.route('/products')
def products():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    if 'skin_type' not in session:
        return redirect(url_for('skin_type'))

    return render_template("products.html", skin_type=session['skin_type'])


@app.route('/product_details/<int:product_id>')
def product_details(product_id): 
    db = get_db()

    produkt = db.execute(
        "SELECT * FROM produkt WHERE id= ?",
        (product_id,)
    ).fetchone()

    shop_domain=""
    if produkt["shop_link"]:
        netloc = urlparse(produkt["shop_link"]).netloc
        shop_domain = netloc.replace("www.","")

    bewertungen = db.execute(
        """SELECT b.sterne, b.kommentar, b.datum, u.name AS user_name FROM bewertung b JOIN benutzer u ON b.benutzer_id = u.id WHERE b.produkt_id = ? ORDER BY b.datum DESC""",
        (product_id,)).fetchall()

    stats = db.execute(""" SELECT AVG(sterne) AS avg_sterne, COUNT(*) AS anzahl FROM bewertung WHERE produkt_id = ?""", 
        (product_id,)).fetchone()

    avg = stats["avg_sterne"] if stats["avg_sterne"] is not None else 0
    count = stats["anzahl"]

    avg_rounded = int(round(avg))

    return render_template(
        "product_details.html",
        produkt=produkt,
        bewertungen=bewertungen,
        avg=avg,
        count=count,
        avg_rounded=avg_rounded,
        shop_domain=shop_domain
    )

#Bewertungen 
@app.route("/products/<int:product_id>/reviews", methods=["POST"])
def add_review(product_id):
    sterne = int(request.form["stars"])
    kommentar = request.form["text"]

    db = get_db()
    benutzer_email = session["user_email"]  

    user_row = db.execute("SELECT id FROM benutzer WHERE email = ?",(benutzer_email,)
     ).fetchone()

    benutzer_id = user_row["id"]

    db.execute("INSERT INTO bewertung (produkt_id, benutzer_id, sterne, kommentar) VALUES (?,?,?,?)", 
               (product_id, benutzer_id, sterne, kommentar)) 
    db.commit()

    return redirect(url_for("product_details", product_id=product_id))
    

@app.route('/favorites')
def favorites():
    return render_template("favorites.html")       


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('login'))
