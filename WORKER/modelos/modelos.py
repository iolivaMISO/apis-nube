from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import LargeBinary

db = SQLAlchemy()


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    password = db.Column(db.String(128))
    email = db.Column(db.String(128))
    tareas = db.relationship('Tarea', cascade='all, delete, delete-orphan')


class Tarea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(128))
    file_name_converted = db.Column(db.String(128))
    file_path = db.Column(db.String(1024))
    file_path_converted = db.Column(db.String(1024))
    time_stamp = db.Column(db.DateTime, default=datetime.utcnow)
    new_format = db.Column(db.String(128))
    status = db.Column(db.String(128), default="uploaded")
    usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'))
