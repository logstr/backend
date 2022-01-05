'''
Create app module and initialization of core packages
'''
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import config
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO

db = SQLAlchemy()
migrate = Migrate()
sio = SocketIO(logger=False, engineio_logger=False)

def create_app(configname):
    """ Core create function app """
    app = Flask(__name__)
    app.config.from_object(config[configname])

    db.init_app(app)
    sio.init_app(app, cors_allowed_origins="*")
    migrate.init_app(app, db, render_as_batch=True)
    CORS(app)
    

    from app.api import api as api_blueprint
    from app import models

    app.register_blueprint(api_blueprint, url_prefix='/api')
    return app

