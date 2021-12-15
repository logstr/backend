'''
Create app module and initialization of core packages
'''
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import config

db = SQLAlchemy()
migrate = Migrate()

def create_app(configname):
    """ Core create function app """
    app = Flask(__name__)
    app.config.from_object(config[configname])

    db.init_app(app)
    migrate.init_app(app, db)

    from app.api import api as api_blueprint
    from app import models

    app.register_blueprint(api_blueprint, url_prefix='/api')
    return app
