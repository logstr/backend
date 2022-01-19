import os
from dotenv import load_dotenv, find_dotenv

load_dotenv()
basedir= os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@localhost/{}'\
        .format(os.getenv('DB_USER'),os.getenv('DB_PASSWORD'), os.getenv('DB_NAME'))
    # 'sqlite:///' + os.path.join(basedir, 'logstr.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    RESTPLUS_VALIDATE = True
    SWAGGER_UI_OPERATION_ID = True
    SWAGGER_UI_REQUEST_DURATION = True
    SWAGGER_UI_DOC_EXPANSION = None
    RESTPLUS_MASK_SWAGGER = True
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT')
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    RQ_REDIS_URL = 'redis://localhost:6379'
    RQ_QUEUES = ['default', 'high', 'medium', 'low']
    RQ_SCHEDULER_QUEUE = 'scheduled'
    RQ_DASHBOARD_REDIS_URL='redis://localhost:6379'
    RQ_DASHBOARD_USERNAME='admin'
    RQ_DASHBOARD_PASSWORD='admin'
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['nitroshark40@gmail.com']


class Development(Config):
    DEBUG = True
    HOST = '127.0.0.1'
    PORT = 5000

class Production(Config):
    DEBUG = False
    HOST = '0.0.0.0'
    PORT = 80


config = {
    'dev': Development,
    'prod': Production,
    'default': Development
}
