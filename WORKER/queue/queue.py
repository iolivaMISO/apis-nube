import io
import shutil
import tarfile
import zipfile
import py7zr
from flask import make_response
from google.cloud import pubsub_v1
from ..modelos import Tarea
from ..app import db
from celery import Celery
from celery.signals import task_postrun

queue = Celery('tasks', broker='google-cloud-pubsub://')

# Configurar credenciales de autenticación para Google Cloud
# Aquí asumimos que las credenciales se cargan de una variable de entorno,
# pero podrían cargarse de otros medios como un archivo de configuración
# o de un servicio de autenticación como Google Cloud SDK.
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/path/to/credentials.json"

# Configurar el identificador del proyecto
project_id = "my-project-id"

# Configurar el nombre del tema de Pub/Sub
topic_name = "my-topic-name"

# Configurar el identificador de la suscripción a Pub/Sub
subscription_name = "my-subscription-name"

# Configurar el cliente de Pub/Sub
publisher_client = pubsub_v1.PublisherClient()
subscriber_client = pubsub_v1.SubscriberClient()

# Configurar el tema de Pub/Sub
topic_path = publisher_client.topic_path(project_id, topic_name)

# Configurar la suscripción a Pub/Sub
subscription_path = subscriber_client.subscription_path(
    project_id, subscription_name
)

@queue.task(name="queque_envio")
def enviar_accion(id, new_format):
    process_to_convert(new_format, id)
    actualizacion_tarea = Tarea.query.filter(Tarea.id == id).first()
    actualizacion_tarea.status = "processed"
    db.session.add(actualizacion_tarea)
    db.session.commit()


@task_postrun.connect
def close_session(*args, **kwargs):
    db.session.remove()


def process_to_convert(new_format, nueva_tarea_id):
    file = get_file_by_id_task(nueva_tarea_id)
    if new_format.upper() == 'TAR.GZ':
        convert_file_tar_gz(nueva_tarea_id, file)
    elif new_format.upper() == '7Z':
        convert_file_7z(nueva_tarea_id, file)
    elif new_format.upper() == 'TAR.BZ2':
        convert_file_tar_bz2(nueva_tarea_id, file)


def get_file_by_id_task(id_task):
    tarea = Tarea.query.get_or_404(id_task)

    with open(tarea.file_path, 'rb') as file:
        return io.BytesIO(file.read())


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
