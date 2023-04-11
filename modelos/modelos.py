from dataclasses import fields
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    password = db.Column(db.String(128))
    email = db.Column(db.String(128))
    tareas = db.relationship('Tarea', cascade='all, delete, delete-orphan')

