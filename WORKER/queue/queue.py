from celery import Celery
from flask import request
from ..modelos import Tarea
from ..app import db
from celery.signals import task_postrun

queue = Celery('tasks', broker='redis://localhost:6379/0')


@queue.task(name="queque_envio")
def enviar_accion(id, filename, new_format, file_name_converted):
    #print(f'Id: {id}')
    #print("nombre archivo"+filename)
    #print("nombre nuevo formato: "+new_format)
    #print("nombre archivo a convertir: "+file_name_converted)
    actualizacion_tarea = Tarea.query.filter(Tarea.id == id).first()
    actualizacion_tarea.status = "processed"
    db.session.add(actualizacion_tarea)
    db.session.commit()

@task_postrun.connect
def close_session(*args, **kwargs):
    db.session.remove()
