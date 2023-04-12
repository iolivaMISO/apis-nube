import os
from operator import concat
from flask import send_file
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from modelos import db, Tarea

FOLDER_IN = concat(os.getcwd(), '/files/IN')


class VistaSignup(Resource):
    def post(self):
        pass


class VistaLogin(Resource):
    def post(self):
        pass


class VistaTask(Resource):
    @jwt_required()
    def get(self, id_task):
        pass

    @jwt_required()
    def delete(self, id_task):
        pass


class VistaTasks(Resource):
    @jwt_required()
    def get(self):
        pass

    @jwt_required()
    def post(self):
        pass


class VistaFiles(Resource):
    @jwt_required()
    def get(self, filename):
        filename = secure_filename(filename)
        tarea = Tarea.query.filter( Tarea.file_name == filename).first()
        return send_file(os.path.join(FOLDER_IN, str(tarea.id), filename))
