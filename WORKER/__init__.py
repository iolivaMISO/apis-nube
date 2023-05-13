from flask import Flask

IP = '10.188.0.4'


def create_app(config_name):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://admin:admin@{IP}:5432/apisnube'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PROPAGATE_EXCEPTIONS'] = True
    return app
