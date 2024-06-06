from flask import Flask, render_template, request, redirect, url_for, session, abort, jsonify, send_file
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import os
import re
from io import BytesIO
from models import db, Users, Barang

import sqlalchemy
app = Flask(__name__)
app.config['SECRET_KEY'] = 'siapa-ini'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://kplesly_owner:MOSGwn3K9ZVE@ep-lively-hat-a1dd4nff.ap-southeast-1.aws.neon.tech/kplesly?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

bcrypt = Bcrypt(app)
db.init_app(app)

with app.app_context():
    db.create_all()

shopping_cart = []
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=['GET', 'POST'])
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
    item = {'id': data['id'], 'nama': data['nama'], 'harga': data['harga'], 'quantity': 1}
    existing_item = next((i for i in shopping_cart if i['id'] == item['id']), None)
    if existing_item:
        existing_item['quantity'] += 1
    else:
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
        user_exists = Users.query.filter_by(email=email).first() is not None
        if user_exists:
            mesage = 'Email already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address!'
        elif not fullname or not password or not email:
            mesage = 'Please fill out the form!'
        else:
            role = 'user'
            if email == 'admin@gmail.com':
                role = 'admin'
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
                if email == 'admin@gmail.com':
                    session['role'] = 'admin'
                else:
                    session['role'] = 'user'
                message = 'Logged in successfully!'
                return redirect(url_for('dashboard'))
    return render_template('login.html', message=message)

@app.route("/dashboard", methods=['GET', 'POST'])
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

@app.route("/barang", methods=['GET', 'POST'])
def barang():
    if 'loggedin' in session and session.get('role') == 'admin':
        barangs = Barang.query.all()
        return render_template("barang.html", barangs=barangs)
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
                if 'picture' in request.files:
                    file = request.files['picture']
                    if file.filename != '' and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        file_data = file.read()
                        barang.picture = filename
                        barang.picture_data = file_data
                        barang.picture_mime_type = file.mimetype
                db.session.commit()
            else:
                file = request.files['picture']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_data = file.read()
                    barang = Barang(nama=nama, harga=harga, stok=stok, picture=filename, picture_data=file_data, picture_mime_type=file.mimetype, kategori=kategori)
                    db.session.add(barang)
                    db.session.commit()
                else:
                    msg = 'Invalid Upload, only png, jpg, jpeg, gif allowed'
            return redirect(url_for('barang'))
        msg = 'Please fill out the form!'
    return redirect(url_for('login'))

@app.route("/edit_barang", methods=['GET', 'POST'])
def edit_barang():
    if 'loggedin' in session:
        barangid = request.args.get('barangid')
        barang = Barang.query.get(barangid)
        return render_template("edit_barang.html", barang=barang)
    return redirect(url_for('login'))

@app.route("/delete_barang", methods=['GET'])
def delete_barang():
    if 'loggedin' in session:
        barangid = request.args.get('barangid')
        barang = Barang.query.get(barangid)
        db.session.delete(barang)
        db.session.commit()
        return redirect(url_for('barang'))
    return redirect(url_for('login'))

@app.route('/images/<int:barang_id>')
def image(barang_id):
    barang = Barang.query.get(barang_id)
    if barang and barang.picture_data:
        return send_file(BytesIO(barang.picture_data), mimetype=barang.picture_mime_type)
    return abort(404)

if __name__ == '__main__':
    app.run(debug=True)
