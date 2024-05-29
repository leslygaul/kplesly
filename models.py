# C:\flask_dev\myapp\models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(50))

class Barang(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100))
    harga = db.Column(db.Integer)
    stok = db.Column(db.Integer)
    kategori = db.Column(db.String(100))
    picture = db.Column(db.String(100))  # Filename for the picture
    picture_data = db.Column(db.LargeBinary)  # Binary data of the picture
    picture_mime_type = db.Column(db.String(50))  # MIME type of the picture

