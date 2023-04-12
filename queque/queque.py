from celery import Celery

queque = Celery('tasks', broker='redis://localhost:6379/0')

@queque.task(name="queque_envio")
def enviar_accion(mensaje, archivo):
    print(mensaje)
    print(archivo)
