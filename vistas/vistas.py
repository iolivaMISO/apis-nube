import hashlib
import io
import os
import shutil
import tarfile
import tempfile
import zipfile
from operator import concat
from flask import send_file, make_response
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from flask import request
from modelos import db, Usuario, Tarea, TareaSchema
import os
from operator import concat
from werkzeug.utils import secure_filename

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
        args = request.args
        query_max = args.get('max') or None
        query_order = args.get('order') or None
        if query_max != None and not query_max.isnumeric():
            return {"mensaje": "max debe ser numerico"}, 400
        if query_order != None and query_order not in ('0', '1'):
            return {"mensaje": "order debe ser numerico: 0 o 1"}, 400
        if (query_order == '1'):
            tareas = Tarea.query.order_by(Tarea.id.desc()).limit(query_max)
        else:
            tareas = Tarea.query.limit(query_max)
        return [tarea_schema.dump(tarea) for tarea in tareas]

    @jwt_required()
    def post(self):
        archivo = request.files['file']
        new_format = request.form["newFormat"]
        if archivo.filename == '':
            return {"mensaje": "file no proporcionado"}
        if not allowed_file(archivo.filename):
            return {"mensaje": "file no soportado"}
        if archivo:
            # convert_file(archivo)
            filename = secure_filename(archivo.filename)
            # file_name_converted = os.path.splitext(filename)[
            #                           0] + '.' + new_format
            current_user = Usuario.query.filter(
                Usuario.username == get_jwt_identity()).first()
            nueva_tarea = Tarea(file_name=filename,
                                new_format=new_format, usuario=current_user.id, file_data_name=archivo.read())
            db.session.add(nueva_tarea)
            db.session.commit()
            tmp_file = getFileByIdTask(nueva_tarea.id)
            convert_file_tar_gz(nueva_tarea.id, tmp_file.name)
        return {"mensaje": "procesado con éxito"}


class VistaFiles(Resource):
    @jwt_required()
    def get(self, filename):
        filename = secure_filename(filename)
        task = Tarea.query.filter(Tarea.file_name == filename).first()
        tmp_file = getFileByIdTask2(task.id)
        filename_new_extension = getFileNameConvertedByTask(task)
        return download_file(tmp_file, filename_new_extension)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].upper() in ALLOWED_EXTENSIONS


def getFileNameConvertedByTask(tarea):
    filename_new_extension = tarea.file_name.replace(".zip", "")
    filename_new_extension = filename_new_extension.rsplit('.', 1)[0] + '.' + tarea.new_format
    filename_new_extension = filename_new_extension.lower()
    return filename_new_extension


def getFileByIdTask(id_task):
    tarea = Tarea.query.get_or_404(id_task)
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(tarea.file_data_name)
        tmp_file.seek(0)
    return tmp_file


def getFileByIdTask2(id_task):
    tarea = Tarea.query.get_or_404(id_task)
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(tarea.file_data_name)
        tmp_file.seek(0)
        file_contents = tmp_file.read()
    return io.BytesIO(file_contents)


def download_file(tmp_file, filename):
    # return the converted file as an attachment
    response = make_response(send_file(tmp_file,
                                       mimetype='application/gzip',
                                       as_attachment=True,
                                       download_name=f'{filename.split(".")[0]}.tar.gz'))
    response.headers['Content-Disposition'] = f'attachment; filename="{filename.split(".")[0]}.tar.gz"'

    return response



def convert_file_tar_gz(id_task, file):
    tarea = Tarea.query.get_or_404(id_task)

    # extract the contents of the ZIP file to a temporary directory
    with zipfile.ZipFile(file, 'r') as zip_ref:
        tmp_dir = 'tmp'
        zip_ref.extractall(tmp_dir)

    # create the TAR.GZ file from the temporary directory
    with tarfile.open('output.tar.gz', 'w:gz') as tar_ref:
        tar_ref.add(tmp_dir, arcname=os.path.basename(tmp_dir))

    # read the TAR.GZ file contents into a bytes variable
    with open('output.tar.gz', 'rb') as output_file:
        file_contents = output_file.read()

    # create a BytesIO object from the file contents
    file_buffer = io.BytesIO(file_contents)

    # update the tarea object with the file contents
    tarea.file_name_converted = file_buffer.getvalue()
    db.session.commit()

    # remove the temporary directory and TAR.GZ file
    shutil.rmtree(tmp_dir)
    os.remove('output.tar.gz')

    # send the TAR.GZ file as a response
    # return send_file('output.tar.gz', as_attachment=True)
