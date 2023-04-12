from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from modelos import db, Usuario, Tarea
import os
from operator import concat
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'ZIP', '7Z', 'TAR.GZ', 'TAR.BZ2'}
FOLDER_IN = concat(os.getcwd(), '/files/IN')
FOLDER_OUT = '/files/OUT'


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
        tarea = Tarea.query.get_or_404(id_task)
        db.session.delete(tarea)
        db.session.commit()
        return '', 204


class VistaTasks(Resource):
    @jwt_required()
    def get(self):
        pass

    @jwt_required()
    def post(self):
        archivo = request.files['file']
        new_format = request.form["newFormat"]
        if archivo.filename == '':
            return {"mensaje": "file no proporcionado"}
        if not allowed_file(archivo.filename):
            return {"mensaje": "file no soportado"}
        if archivo:
            filename = secure_filename(archivo.filename)
            file_name_converted = os.path.splitext(filename)[
                0]+'.'+new_format
            current_user = Usuario.query.filter(
                Usuario.username == get_jwt_identity()).first()
            nueva_tarea = Tarea(file_name=filename, file_name_converted=file_name_converted,
                                new_format=new_format, usuario=current_user.id)
            db.session.add(nueva_tarea)
            db.session.commit()
            filename = os.path.join(
                FOLDER_IN, str(nueva_tarea.id), filename)

            root_folder = os.path.dirname(filename)
            os.makedirs(root_folder, exist_ok=True)
            archivo.save(filename)
        return {"mensaje": "procesado con éxito"}


class VistaFiles(Resource):
    @jwt_required()
    def get(self, filename):
        pass


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].upper() in ALLOWED_EXTENSIONS
