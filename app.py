from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from .vistas import VistaSignup, VistaLogin, VistaFiles, VistaTask, VistaTasks
from .modelos import db
from . import create_app

app = create_app('default')
app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

api = Api(app)

api.add_resource(VistaSignup, '/api/auth/signup')
api.add_resource(VistaLogin, '/api/auth/login')
api.add_resource(VistaTask,  '/api/tasks/<int:id_task>')
api.add_resource(VistaTasks,  '/api/tasks')
api.add_resource(VistaFiles, '/api/files/<filename>')

jwt = JWTManager(app)