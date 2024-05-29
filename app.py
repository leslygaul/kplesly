#C:\flask_dev\myapp\app.py
from flask import Flask, render_template, request, redirect, url_for, session, abort, jsonify
from flask_bcrypt import Bcrypt #pip install Flask-Bcrypt = https://pypi.org/project/Flask-Bcrypt/
from werkzeug.utils import secure_filename
import os
import re
import sqlalchemy
from models import db, Users, Barang
   
app = Flask(__name__)
    
app.config['SECRET_KEY'] = 'siapa-ini'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flaskdb.db'
# Databse configuration mysql                             Username:password@hostname/databasename
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://kplesly_owner:MOSGwn3K9ZVE@ep-lively-hat-a1dd4nff.ap-southeast-1.aws.neon.tech/kplesly?sslmode=require'
  
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True
   
bcrypt = Bcrypt(app) 
  
db.init_app(app)
         
with app.app_context():
    db.create_all()
 
 
app.config['UPLOAD_FOLDER'] = 'postgresql://kplesly_owner:MOSGwn3K9ZVE@ep-lively-hat-a1dd4nff.ap-southeast-1.aws.neon.tech/kplesly?sslmode=require'

shopping_cart = []
    
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
    
def allowed_file(filename):
 return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 
@app.route("/", methods =['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/shop')
def shop():
    barangs = Barang.query.all()
    return render_template('clients.html', barangs=barangs)


@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()

    item = {
        'id': data['id'],
        'nama': data['nama'],
        'harga': data['harga'],
        'quantity': 1  # Default quantity set to 1
    }

    # Cek apakah item sudah ada di keranjang
    existing_item = next((i for i in shopping_cart if i['id'] == item['id']), None)

    if existing_item:
        # Jika item sudah ada, tambahkan jumlahnya
        existing_item['quantity'] += 1
    else:
        # Jika item belum ada, tambahkan ke keranjang
        shopping_cart.append(item)

    return jsonify({'status': 'success'})

@app.route('/get-cart', methods=['GET'])
def get_cart():
    return jsonify(shopping_cart)

@app.route('/register', methods=['GET', 'POST'])
def register():
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form:
        fullname = request.form['name']
        password = request.form['password']
        email = request.form['email']
        
        # Check if the email already exists
        user_exists = Users.query.filter_by(email=email).first() is not None
        
        if user_exists:
            mesage = 'Email already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address!'
        elif not fullname or not password or not email:
            mesage = 'Please fill out the form!'
        else:
            # Assign the default role
            role = 'user'
            
            # Check if a special condition is met (e.g., specific email address) to assign the 'admin' role
            if email == 'admin@gmail.com':
                role = 'admin'
            
            # hashed_password = bcrypt.generate_password_hash(password)
            new_user = Users(name=fullname, email=email, password=password, role=role)
            
            db.session.add(new_user)
            db.session.commit()
            mesage = 'You have successfully registered!'
    elif request.method == 'POST':
        mesage = 'Please fill out the form!'
    return render_template('register.html', mesage=mesage)

     
@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email == '' or password == '':
            message = 'Please enter email and password!'
        else:
            user = Users.query.filter_by(email=email).first()

            if user is None:
                message = 'Please enter correct email/password!'
            else:
                session['loggedin'] = True
                session['userid'] = user.id
                session['name'] = user.name
                session['email'] = user.email

                    # Set the 'role' based on email
                if email == 'admin@gmail.com':
                    session['role'] = 'admin'
                else:
                    session['role'] = 'user'

                message = 'Logged in successfully!'
                return redirect(url_for('dashboard'))
                # if not bcrypt.check_password_hash(user.password, password):
                #     message = 'Please enter correct email and password!'
                # else:
                #     session['loggedin'] = True
                #     session['userid'] = user.id
                #     session['name'] = user.name
                #     session['email'] = user.email

                #     # Set the 'role' based on email
                #     if email == 'admin@gmail.com':
                #         session['role'] = 'admin'
                #     else:
                #         session['role'] = 'user'

                #     message = 'Logged in successfully!'
                #     return redirect(url_for('dashboard'))

    return render_template('login.html', message=message)

 
@app.route("/dashboard", methods =['GET', 'POST'])
def dashboard():
    if 'loggedin' in session:        
        return render_template("dashboard.html")
    return redirect(url_for('login'))   
 
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))
 
# Manage Barang
@app.route("/barang", methods=['GET', 'POST'])
def barang():
    if 'loggedin' in session:
        # Check if the user has the "admin" role
        if 'role' in session and session['role'] == 'admin':
            barangs = Barang.query.all()
            return render_template("barang.html", barangs=barangs)
        else:
            # If the user doesn't have the "admin" role, abort with a 403 Forbidden error
            abort(403)
    return redirect(url_for('login'))

@app.route('/save_barang', methods=['POST'])
def save_barang():
    msg = ''
    if 'loggedin' in session:
        if request.method == 'POST':
            nama = request.form['nama']
            harga = request.form['harga']
            stok = request.form['stok']
            kategori = request.form['kategori']
            action = request.form['action']

            if action == 'updateBarang':
                barangid = request.form['barangid']
                barang = Barang.query.get(barangid)

                barang.nama = nama
                barang.harga = harga
                barang.stok = stok
                barang.kategori = kategori

                # Check if a new image is uploaded
                if 'picture' in request.files:
                    file = request.files['picture']
                    if file.filename != '' and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        barang.picture = filename
                # Commit changes to the database
                db.session.commit()
                print("UPDATE barang")
            else:
                file = request.files['picture']
                filename = secure_filename(file.filename)
                print(filename)
                if file and allowed_file(file.filename):
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    filenameimage = file.filename

                    barang = Barang(nama=nama, harga=harga, stok=stok, picture=filenameimage, kategori=kategori)
                    db.session.add(barang)
                    db.session.commit()
                    print("INSERT INTO barang")
                else:
                    msg = 'Invalid Upload, only png, jpg, jpeg, gif allowed'
            return redirect(url_for('barang'))
        elif request.method == 'POST':
            msg = 'Please fill out the form!'
        return render_template("barang.html", msg=msg)
    return redirect(url_for('login'))


@app.route("/edit_barang", methods=['GET', 'POST'])
def edit_barang():
    msg = ''
    if 'loggedin' in session:
        barangid = request.args.get('barangid')
        print(barangid)
        barang = Barang.query.get(barangid)

        return render_template("edit_barang.html", barang=barang)
    return redirect(url_for('login'))

@app.route("/delete_barang", methods=['GET'])
def delete_barang():
    if 'loggedin' in session:
        barangid = request.args.get('barangid')
        barang = Barang.query.get(barangid)
        print(barang.picture)
        db.session.delete(barang)
        db.session.commit()
        os.unlink(os.path.join(app.config['UPLOAD_FOLDER'], barang.picture))
        return redirect(url_for('barang'))
    return redirect(url_for('login'))

if __name__=='__main__':
    app.run(debug=True)