import os
import bcrypt
from flask import Flask, render_template, redirect, url_for, session, request, flash, abort
from urllib.parse import urlparse
from sqlalchemy import func


app = Flask(__name__)
app.secret_key = "supersecretkey"


from db import db, Benutzer, Produkt, Kategorie, Hauttyp, Bewertung, insert_sample


@app.route('/')
def index():
    return render_template ('home.html')



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        user = db.session.execute(
            db.select(Benutzer).where(Benutzer.email == email)
        ).scalar_one_or_none()

        if user is None:
            flash("Email oder Passwort ist falsch.", "login")
            return redirect(url_for("login"))

        if not bcrypt.checkpw(password.encode("utf-8"), user.passwort_hash.encode("utf-8")):
            flash("Email oder Passwort ist falsch.", "login")
            return redirect(url_for("login"))

        session.clear()
        session["user_id"] = user.id
        session["username"] = user.name
        session["skin_type"] = user.hauttyp_id

        return redirect(url_for("products"))

    return render_template("login.html")
       



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        if not username or not email or not password:
            flash("Bitte alle Felder ausfüllen.", "register")
            return redirect(url_for("register"))

        
        exists_email = db.session.execute(
            db.select(Benutzer).where(Benutzer.email == email)
        ).scalar_one_or_none()

        if exists_email:
            flash("Diese Email ist bereits registriert.", "register")
            return redirect(url_for("register"))

        exists_name = db.session.execute(
            db.select(Benutzer).where(Benutzer.name == username)
        ).scalar_one_or_none()

        if exists_name:
            flash("Username existiert bereits.", "register")
            return redirect(url_for("register"))

        pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        user = Benutzer(
            name=username,
            email=email,
            passwort_hash=pw_hash,
            hauttyp_id=1  # oder später None + nach skin_type setzen
        )

        db.session.add(user)
        db.session.commit()

        session.clear()
        session["user_id"] = user.id
        session["username"] = user.name

        return redirect(url_for("skin_type"))

    return render_template("register.html")

   
@app.route('/skin_type', methods=['GET', 'POST'])
def skin_type():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_id = int(request.form['skin_type'])

        session['skin_type'] = new_id
        user= db.session.get(Benutzer, session["user_id"])
        if user:
            user.hauttyp_id = new_id
            db.session.commit()

        return redirect(url_for('products'))


    hauttypen = db.session.execute(
        db.select(Hauttyp).order_by(Hauttyp.id)
    ).scalars().all()

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

    selected_skin_type = session.get("skin_type")
    if not selected_skin_type:
        selected_skin_type = user.hauttyp_id

    q = db.select(Produkt).where(
        Produkt.geeignet_fuer.any(Hauttyp.id == selected_skin_type)
    )

    if selected_category:
        q = q.where(
            Produkt.kategorien.any(Kategorie.id == selected_category)
        )

    produkte = db.session.execute(q).scalars().all()
    favorite_ids = {p.id for p in user.favoriten}

    # -------- image_map --------
    image_map = {}
    base = os.path.join(app.static_folder, "images", "products")

    for root, dirs, files in os.walk(base):
        for f in files:
            if f.lower().endswith((".png", ".jpg", ".jpeg")):
                rel = os.path.relpath(
                    os.path.join(root, f),
                    app.static_folder
                )
                image_map[f] = rel.replace("\\", "/")

    # -------- Info Box (Kategorie-basiert) --------
    if selected_category:
        cat = db.session.get(Kategorie, selected_category)
        info_title = cat.bezeichnung
        info_text = cat.beschreibung
    else:
        info_title = "Alle Produkte"
        info_text = "Hier findest du alle Produkte, die zu deinem Hauttyp passen."

    return render_template(
    "products.html",
    products=produkte,
    categories=kategorien,
    selected_category=selected_category,
    favorite_ids=favorite_ids,
    image_map=image_map,
    info_title=info_title,
    info_text=info_text,

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
    if "user_id" not in session:
        return redirect(url_for("login"))

    sterne = int(request.form["stars"])
    kommentar = request.form["text"].strip()

    benutzer = db.session.get(Benutzer,session["user_id"])
    if benutzer is None:
        session.clear()
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
    return redirect(url_for('index'))


@app.route('/insert/sample')
def run_insert_sample():
    insert_sample()
    return 'Database flushed and populated with some sample data.'


