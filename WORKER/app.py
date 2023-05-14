from flask import Flask

from . import create_app
from .modelos import db, Tarea
import io
import shutil
import tarfile
import zipfile
import py7zr
from google.cloud import pubsub_v1

app = create_app('default')
app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

app = Flask(__name__)


project_id = 'api-nube-semana-3'
topic_name = 'my-topic'
subscriber_name = 'my-subscriber'
topic_path = f"projects/{project_id}/topics/{topic_name}"

def convert_file_tar_gz(id_task, file):
    tarea = Tarea.query.get_or_404(id_task)
    # extract the contents of the ZIP file to a temporary directory
    with zipfile.ZipFile(file, 'r') as zip_ref:
        tmp_dir = 'tmp'
        zip_ref.extractall(tmp_dir)

    # create the TAR.GZ file from the temporary directory
    with io.BytesIO() as tar_buffer:
        with tarfile.open(fileobj=tar_buffer, mode='w:gz') as tar_ref:
            tar_ref.add(tmp_dir, arcname='.')

        # get the bytes of the TAR.GZ file
        tar_bytes = tar_buffer.getvalue()
    with open(tarea.file_path_converted, 'wb') as archivo:
        archivo.write(tar_bytes)
    # tarea.file_data_converted = tar_bytes
    # db.session.commit()

    # delete the temporary directory
    shutil.rmtree(tmp_dir)


def convert_file_tar_bz2(id_task, file):
    tarea = Tarea.query.get_or_404(id_task)

    # extract the contents of the ZIP file to a temporary directory
    with zipfile.ZipFile(file, 'r') as zip_ref:
        tmp_dir = 'tmp'
        zip_ref.extractall(tmp_dir)

    # create the TAR.BZ2 file from the temporary directory
    with io.BytesIO() as tar_buffer:
        with tarfile.open(fileobj=tar_buffer, mode='w:bz2') as tar_ref:
            tar_ref.add(tmp_dir, arcname='.')

        # get the bytes of the TAR.BZ2 file
        tar_bytes = tar_buffer.getvalue()

    with open(tarea.file_path_converted, 'wb') as archivo:
        archivo.write(tar_bytes)
    # tarea.file_data_converted = tar_bytes
    # db.session.commit()

    # delete the temporary directory
    shutil.rmtree(tmp_dir)


def convert_file_7z(id_task, file):
    tarea = Tarea.query.get_or_404(id_task)
    # extract the contents of the ZIP file to a temporary directory
    with zipfile.ZipFile(file, 'r') as zip_ref:
        tmp_dir = 'tmp'
        zip_ref.extractall(tmp_dir)

    # create the 7Z file from the temporary directory
    with io.BytesIO() as archive_buffer:
        with py7zr.SevenZipFile(archive_buffer, 'w') as archive_ref:
            archive_ref.writeall(tmp_dir)

        # get the bytes of the 7Z file
        archive_bytes = archive_buffer.getvalue()
    with open(tarea.file_path_converted, 'wb') as archivo:
        archivo.write(archive_bytes)
    # tarea.file_data_converted = archive_bytes
    # db.session.commit()

    # delete the temporary directory
    shutil.rmtree(tmp_dir)

def get_file_by_id_task(id_task):
    tarea = Tarea.query.get_or_404(id_task)

    with open(tarea.file_path, 'rb') as file:
        return io.BytesIO(file.read())

def process_to_convert(new_format, nueva_tarea_id):
    file = get_file_by_id_task(nueva_tarea_id)
    if new_format.upper() == 'TAR.GZ':
        convert_file_tar_gz(nueva_tarea_id, file)
    elif new_format.upper() == '7Z':
        convert_file_7z(nueva_tarea_id, file)
    elif new_format.upper() == 'TAR.BZ2':
        convert_file_tar_bz2(nueva_tarea_id, file)


def enviar_accion(id, new_format):
    process_to_convert(new_format, id)
    actualizacion_tarea = Tarea.query.filter(Tarea.id == id).first()
    actualizacion_tarea.status = "processed"
    db.session.add(actualizacion_tarea)
    db.session.commit()


def callback(message):
    print("calbackkkkk")
    print(f"Mensaje recibido: {message.data.decode()}")
    print("Legoooooooooooooooooooo " + str(message.data.decode()))
    print(message.data)
    # Realiza cualquier procesamiento adicional que desees hacer con el mensaje aquí
    data = str(message.data.decode()).split(",")
    print(data[0])
    print(data[1])
    enviar_accion(data[0], data[1])
    message.ack()  # Confirma la recepción del mensaje


def subscribe():
    # Crea un cliente de Pub/Sub
    subscriber = pubsub_v1.SubscriberClient()

    # Crea el nombre completo de la suscripción
    subscription_path = f"projects/{project_id}/subscriptions/{subscriber_name}"

    # Inicia la suscripción y especifica la función de devolución de llamada
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)

    # Espera a que la suscripción se mantenga activa
    try:
        streaming_pull_future.result()
    except Exception as e:
        streaming_pull_future.cancel()
        raise

subscribe()
