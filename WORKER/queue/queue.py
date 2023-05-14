import io
import shutil
import tarfile
import zipfile
import py7zr
from celery import Celery
from google.cloud import pubsub_v1
from flask import make_response

from ..modelos import Tarea
from ..app import db
from celery.signals import task_postrun

import os
from google.cloud import pubsub_v1


queue = Celery('tasks', broker='pubsub://', backend='rpc://')

project_id = 'api-nube-semana-3'
topic_name = 'my-topic'
subscriber_name = 'my-subscriber'

topic_name = 'projects/'+ project_id +'/topics/'+topic_name.format(
    project_id=project_id,
    topic=topic_name,  # Set this to something appropriate.
)
subscription_name = 'projects/'+ project_id +'/subscriptions/'+subscriber_name.format(
    project_id=project_id,
    sub=subscriber_name,  # Set this to something appropriate.
)

#subscriber_max_messages = 10

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_name)

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscriber_name)

# Crear la suscripción si no existe
#subscriber.create_subscription(request={"name": subscription_path, "topic": topic_path})


def callback(message):
    print(message.data)
    message.ack()

with pubsub_v1.SubscriberClient() as subscriber:
    subscriber.create_subscription(
        name=subscription_name, topic=topic_name)
    future = subscriber.subscribe(subscription_name, callback)
    try:
        print ("despues del print ",future.result())
    except Exception as e:
        future.cancel()
        raise


# def enviar_accion():
#
#
#     process_to_convert(new_format, id)
#     actualizacion_tarea = Tarea.query.filter(Tarea.id == id).first()
#     actualizacion_tarea.status = "processed"
#     db.session.add(actualizacion_tarea)
#     db.session.commit()


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
