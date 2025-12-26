from flask import Flask, render_template, request, redirect, url_for, flash, session


app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flash messages

users = {} 

@app.route('/')
def index():
    return render_template ('home.html')

@app.route('/login' , methods=['GET', 'POST'])
def login():
    # Wenn schon eingeloggt → direkt zur Hauptseite
    if "user_email" in session:
        return redirect(url_for("index"))

    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']

        # ✅ Prüfen gegen users-Dict (statt test@example)
        if email in users and users[email]["password"] == password:
            session["user_email"] = email
            session["username"] = users[email]["username"]
            flash("Login successful!")
            return redirect(url_for('index'))

        flash("Invalid credentials. Please try again.")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Wenn schon eingeloggt: nicht nochmal registrieren
    if 'user_email' in session:
        return redirect(url_for('index'))

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
        return redirect(url_for('index'))  

    return render_template('register.html')

    
   
@app.route('/skin_type')
def skin_type():
    return "skin_type Screen (Placeholder)"   

@app.route('/products')
def products():
    return "products Screen (placeholder)"  

@app.route('/product_details/<product_id>')
def product_details(product_id):
    return "product_detail Screen for {product_id} (placeholder)"     

@app.route('/favorites')
def favorites():
    return "favorites Screen (placeholder)"       


