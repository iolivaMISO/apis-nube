from modelos import Tarea, db
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from flask import request


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    password = db.Column(db.String(128))
    email = db.Column(db.String(128))
    tareas = db.relationship('Tarea', cascade='all, delete, delete-orphan')

class VistaTask(Resource):
    def put(self, id_task):
        actualizacion_tarea = Tarea.query.filter(Tarea.id == id_task).first()
        actualizacion_tarea.status = "processed"
        db.session.add(actualizacion_tarea)
        db.session.commit()
