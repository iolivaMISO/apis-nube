from flask import Flask

IP = 'localhost'
UPLOAD_FOLDER = '/path/to/the/uploads'


def create_app(config_name):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://admin:admin@{IP}:5432/apisnube'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'uniandes-cloud-class-2023'
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    return app
