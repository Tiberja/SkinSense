import os
from flask import Flask, render_template, redirect, url_for, session, request, flash, abort
from urllib.parse import urlparse
from sqlalchemy import func


app = Flask(__name__)
app.secret_key = "supersecretkey"


from db import db, Benutzer, Produkt, Kategorie, Hauttyp, Bewertung, insert_sample


@app.route('/')
def index():
   # if 'user_id' not in session:
        #return redirect(url_for('login'))
    return render_template ('home.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["username"].strip()

        user = db.session.execute(
            db.select(Benutzer).where(Benutzer.name == name)
        ).scalar_one_or_none()

        if user is None:
            flash("User nicht gefunden. Bitte registrieren.")
            return redirect(url_for("register"))

        session["user_id"] = user.id
        session["username"] = user.name

        return redirect(url_for("products"))

    return render_template("login.html")
       


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not email or not password:
            flash("Bitte alle Felder ausfüllen.")
            return redirect(url_for("register"))

        # Username prüfen
        exists = db.session.execute(
            db.select(Benutzer).where(Benutzer.name == username)
        ).scalar_one_or_none()

        if exists:
            flash("Username existiert bereits.")
            return redirect(url_for("register"))

        user = Benutzer(
            name=username,
            email=email,
            passwort_hash=password,  
            hauttyp_id=1               
        )

        db.session.add(user)
        db.session.commit()

        session["user_id"] = user.id
        session["username"] = user.name

        return redirect(url_for("skin_type"))

    return render_template("register.html")

   
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


@app.route("/products")
def products():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db.session.get(Benutzer, session["user_id"])
    if user is None:
        session.clear()
        return redirect(url_for("login"))

    kategorien = db.session.execute(
        db.select(Kategorie).order_by(Kategorie.id)
    ).scalars().all()

    selected_category = request.args.get("category", type=int)

    q = db.select(Produkt).where(
        Produkt.geeignet_fuer.any(Hauttyp.id == user.hauttyp_id)
    )

    if selected_category:
        q = q.where(Produkt.kategorien.any(Kategorie.id == selected_category))

    produkte = db.session.execute(q).scalars().all()
    favorite_ids = {p.id for p in user.favoriten}


    image_map = {}
    base = os.path.join(app.static_folder, "images", "products")
    for root, dirs, files in os.walk(base):
        for f in files:
            if f.lower().endswith((".png", ".jpg", ".jpeg")):
                rel = os.path.relpath(os.path.join(root, f), app.static_folder)
                image_map[f] = rel.replace("\\", "/")

    return render_template(
        "products.html",
        products=produkte,
        categories=kategorien,
        selected_category=selected_category,
        favorite_ids=favorite_ids,
        image_map=image_map,  
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


@app.route("/favorites")
def favorites():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db.session.get(Benutzer, session["user_id"])

    if user is None:
        session.clear()
        return redirect(url_for("login"))

    fav_products = list(user.favoriten)
    favorite_ids = {p.id for p in user.favoriten}

    return render_template(
        "favorites.html",
        products=fav_products,
        favorite_ids=favorite_ids
    )

@app.post("/favorites/toggle/<int:product_id>")
def toggle_favorite(product_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db.session.get(Benutzer, session["user_id"])
    produkt = db.session.get(Produkt, product_id)

    if not user or not produkt:
        return redirect(url_for("products"))

    if produkt in user.favoriten:
        user.favoriten.remove(produkt)
    else:
        user.favoriten.append(produkt)

    db.session.commit()
    return redirect(request.referrer or url_for("products"))


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('login'))


@app.route('/insert/sample')
def run_insert_sample():
    insert_sample()
    return 'Database flushed and populated with some sample data.'


