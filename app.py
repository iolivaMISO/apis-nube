from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from vistas import VistaSignup, VistaLogin, VistaFiles, VistaTask, VistaTasks
from modelos import db

UPLOAD_FOLDER = '/path/to/the/uploads'
IP='192.168.1.33'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://admin:admin@{IP}:5432/apisnube'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'uniandes-cloud-class-2023'
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
