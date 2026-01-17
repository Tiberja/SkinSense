import os
from flask import Flask, render_template, redirect, url_for, session, request, flash, abort
from urllib.parse import urlparse
from sqlalchemy import func


app = Flask(__name__)
app.secret_key = "supersecretkey"


from db import db, Benutzer, Produkt, Kategorie, Hauttyp, Bewertung, insert_sample


users = {} 



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
    #if 'user_email' not in session:
       # return redirect(url_for('login'))

    if request.method == 'POST':
        session['skin_type'] = int(request.form['skin_type'])
        return redirect(url_for('products'))

    hauttypen = db.session.execute(
        db.select(Hauttyp).order_by(Hauttyp.id)
    ).scalars().all()

    print("DEBUG hauttypen:", [(h.id, h.bezeichnung) for h in hauttypen])


    return render_template('skin_type.html', hauttypen=hauttypen)


@app.route('/products')
def products():
    if 'user_email' not in session:
        return redirect(url_for('login'))

  #  if 'skin_type' not in session:
   #     return redirect(url_for('skin_type'))
   
    user = Benutzer.query.filter_by(email=session["user_email"]).first()

    kategorien = Kategorie.query.order_by(Kategorie.id).all()
    selected_category = request.args.get("category", type=int)

    query = Produkt.query

    if selected_category:
        query = query.filter(
            Produkt.kategorien.any(Kategorie.id == selected_category)
        )

    produkte = query.all()

    return render_template(
        "products.html",
         #, skin_type=session['skin_type',
       
        products=produkte,
        categories=kategorien,
        selected_category=selected_category
    )


@app.route('/product_details/<int:product_id>')
def product_details(product_id): 

    produkt = db.session.execute(
        db.select(Produkt).where(Produkt.id == product_id)
    ).scalar_one_or_none()

    if produkt is None:
        abort(404)

# Shop-Domain aus URL ableiten
    shop_domain=""
    if produkt.shop_link:
        netloc = urlparse(produkt.shop_link).netloc
        shop_domain = netloc.replace("www.","")

# Bewertungen holen
    rows = db.session.execute(
        db.select(Bewertung, Benutzer.name).join(Benutzer, Bewertung.benutzer_id == Benutzer.id).where(Bewertung.produkt_id == product_id).order_by(Bewertung.datum.desc())
    ).all()

    bewertungen = [
        {
            "sterne": bew.sterne,
            "kommentar": bew.kommentar,
            "datum": bew.datum,
            "user_name": user_name,
        }
        for (bew, user_name) in rows
    ]

    avg, count = db.session.execute(
        db.select(func.avg(Bewertung.sterne), func.count(Bewertung.id))
          .where(Bewertung.produkt_id == product_id)
    ).one()

    avg = float(avg) if avg is not None else 0.0
    count = int(count)
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
    if "user_email" not in session:
        return redirect(url_for("login"))

    sterne = int(request.form["stars"])
    kommentar = request.form["text"].strip()

    benutzer = db.session.execute(
        db.select(Benutzer).where(Benutzer.email == session["user_email"])
    ).scalar_one_or_none()

    if benutzer is None:
        flash("Benutzer nicht gefunden. Bitte nochmal einloggen")
        return redirect(url_for("login"))

    bewertung = Bewertung(
        produkt_id=product_id,
        benutzer_id=benutzer.id,
        sterne=sterne,
        kommentar=kommentar
    )

    db.session.add(bewertung)
    db.session.commit()

    return redirect(url_for("product_details", product_id=product_id))


@app.route('/favorites')
def favorites():
    return render_template("favorites.html")       


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('login'))

