#C:\flask_dev\myapp\models.py
from flask_sqlalchemy import SQLAlchemy
          
db = SQLAlchemy()
          
class Users(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), index=True, unique=True)
    email = db.Column(db.String(150), index=True, unique=True)
    password = db.Column(db.String(255), index=True, unique=True)
    role = db.Column(db.String(50))

class Barang(db.Model):
    __tablename__ = "barang"
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    harga = db.Column(db.Float, nullable=False)
    stok = db.Column(db.Integer, nullable=False)
    picture = db.Column(db.String(150), index=True, unique=True)
    kategori = db.Column(db.String(50), nullable=False)