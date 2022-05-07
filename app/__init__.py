'''
Create app module and initialization of core packages
'''
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from config import config
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO
from flask_oauthlib.client import OAuth
from redis import Redis
import rq, rq_dashboard
from flask_mail import Mail



db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
oauth = OAuth()
mail = Mail()
sio = SocketIO(logger=False, engineio_logger=False)

def create_app(configname):
    app = Flask(__name__)
    app.config.from_object(config[configname])

    db.init_app(app)
    sio.init_app(app, cors_allowed_origins="*")
    ma.init_app(app)
    mail.init_app(app)
    oauth.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    app.redis = Redis.from_url(app.config['RQ_REDIS_URL'])
    app.high_queue = rq.Queue('high', connection=app.redis)
    CORS(app)

    from app.api import api as api_blueprint
    from app.webhook import webhook as webhook_blueprint

    app.register_blueprint(api_blueprint, url_prefix='/api')
    app.register_blueprint( webhook_blueprint, url_prefix='/webhook')
    app.register_blueprint(rq_dashboard.blueprint, url_prefix="/api/rq")


    return app

