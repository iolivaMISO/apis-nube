from flask import Flask

from . import create_app
from .queue import db

app = create_app('default')
app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

app = Flask(__name__)
