import hashlib
import os
from operator import concat

from celery import Celery
from flask import send_file
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from flask import request
from modelos import db, Usuario, Tarea, TareaSchema
import os
from operator import concat
from werkzeug.utils import secure_filename

queque = Celery(__name__, broker='redis://localhost:6379')


@queque.task(name="queque_envio")
def enviar_accion(id,filename,new_format,file_name_converted):
    pass


ALLOWED_EXTENSIONS = {'ZIP', '7Z', 'TAR.GZ', 'TAR.BZ2'}
FOLDER_IN = concat(os.getcwd(), '/files/IN')
FOLDER_OUT = '/files/OUT'

tarea_schema = TareaSchema()


class VistaSignup(Resource):
    def post(self):

        username = request.json["username"]
        password1 = request.json["password1"]
        password2 = request.json["password2"]
        email = request.json["email"]
        if password1 != password2:
            return {"mensaje": "la cuenta no pudo ser creada, passwords proporcionados no coinciden."}, 404
        if len(password1) < 8:
            return {"mensaje": "la cuenta no pudo ser creada, longitud de password debe ser mayor a 8 caracteres."}, 404
        usuario = Usuario.query.filter(Usuario.username == username).first()
        if usuario is not None:
            return {"mensaje": "la cuenta no pudo ser creada, username ya existe."}, 404
        usuario = Usuario.query.filter(Usuario.email == email).first()
        if usuario is not None:
            return {"mensaje": "la cuenta no pudo ser creada, email ya existe."}, 404
        password_encriptado = hashlib.md5(
            request.json["password1"].encode('utf-8')).hexdigest()
        nuevo_usuario = Usuario(
            username=username, password=password_encriptado, email=email)
        db.session.add(nuevo_usuario)
        db.session.commit()
        return {"mensaje": "cuenta creada con éxito"}, 200


class VistaLogin(Resource):
    def post(self):
        username = request.json.get("username", None)
        email = request.json.get("email", None)
        password_encriptado = hashlib.md5(
            request.json["password"].encode('utf-8')).hexdigest()

        if email is not None:
            usuario = Usuario.query.filter(
                Usuario.email == email, Usuario.password == password_encriptado).first()
            db.session.commit()
            if usuario is None:
                return {"mensaje": "cuenta no existe"}, 404
        elif username is not None:
            usuario = Usuario.query.filter(
                Usuario.username == username, Usuario.password == password_encriptado).first()
            db.session.commit()
            if usuario is None:
                return {"mensaje": "cuenta no existe"}, 404
        else:
            # Handle the case where email is None
            return {"mensaje": "correo electrónico no proporcionado"}, 400

        token_acceso = create_access_token(identity=usuario.username)
        return {"token": token_acceso}, 200


class VistaTask(Resource):
    @jwt_required()
    def get(self, id_task):
        return tarea_schema.dump(Tarea.query.get_or_404(id_task))
    

    @jwt_required()
    def delete(self, id_task):
        tarea = Tarea.query.get_or_404(id_task)
        db.session.delete(tarea)
        db.session.commit()
        return '', 204


class VistaTasks(Resource):
    @jwt_required()
    def get(self):
        return tarea_schema.dump(Tarea.query.get_or_404(id_task))

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
                                      0] + '.' + new_format
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
            enviar_accion.apply_async(
            (nueva_tarea.id,filename,new_format,file_name_converted))
        return {"mensaje": "procesado con éxito"}


class VistaFiles(Resource):
    @jwt_required()
    def get(self, filename):
        filename = secure_filename(filename)
        tarea = Tarea.query.filter(Tarea.file_name == filename).first()
        return send_file(os.path.join(FOLDER_IN, str(tarea.id), filename))


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].upper() in ALLOWED_EXTENSIONS
