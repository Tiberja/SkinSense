from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "SkinSense - Home Screen (placeholder)"

@app.route('/login')
def login():
    return "Login Screen (placeholder)"

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


