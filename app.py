from flask import Flask, render_template, request, redirect, url_for, flash


app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flash messages

@app.route('/')
def index():
    return "SkinSense - Home Screen (placeholder)"

@app.route('/login' , methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle login logic here
        email = request.form['email']
        password = request.form['password']
       
        # Authenticate user (placeholder logic)
        if email == "test @example.com" and password == "123":
            flash("Login successful!")
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials. Please try again.")
    return render_template('login.html')

@app.route('/register')
def register():
    return "Register Screen (placeholder)"    

@app.route('/skin-type')
def skin_type():
    return "Select Skin Type Screen (Placeholder)"   

@app.route('/products')
def products():
    return "Product List Screen (placeholder)"  

@app.route('/favorites')
def favorites():
    return "Favorites Screen (placeholder)"       


