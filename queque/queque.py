from celery import Celery
from modelos import Tarea
from app import db


queque = Celery('tasks', broker='redis://localhost:6379/0')

@queque.task(name="queque_envio")
def enviar_accion(id,filename,new_format,file_name_converted):
    print(f'Id: {id}')
    print("nombre archivo"+filename)
    print("nombre nuevo formato: "+new_format)
    print("nombre archivo a convertir: "+file_name_converted)
    # actualizacion_tarea = Tarea.query.filter(Tarea.id == id).first()
    #actualizacion_tarea.status = "processed"
    nueva_tarea = Tarea(file_name=filename, file_name_converted=file_name_converted,
                              new_format=new_format)
    db.session.add(nueva_tarea)
    db.session.commit()

