import os
from dotenv import load_dotenv, find_dotenv

load_dotenv()
basedir= os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DB_URI')
    #'postgresql+psycopg2://{}:{}@db/{}'\
    #    .format(os.getenv('DB_USER'),os.getenv('DB_PASSWORD'), os.getenv('DB_NAME'))
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
    RQ_REDIS_URL = os.getenv('RQ_REDIS_URL')
    RQ_QUEUES = ['default', 'high', 'medium', 'low']
    RQ_SCHEDULER_QUEUE = 'scheduled'
    RQ_DASHBOARD_REDIS_URL= os.getenv('RQ_DASHBOARD_REDIS_URL')
    RQ_DASHBOARD_USERNAME='admin'
    RQ_DASHBOARD_PASSWORD='admin'
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['nitroshark40@gmail.com']
    STRIPE_PLANS = {
        '0': {
            'id': 'Professional',
            'name': 'pro',
            'amount': 100,
            'currency': 'usd',
            'interval': 'month',
            'interval_count': 1,
            'trial_period_days': 10,
            'statement_descriptor': 'PROFESSIONAL MONTHLY PLAN'
        },
        '1': {
            'id': 'Team',
            'name': 'Team',
            'amount': 500,
            'currency': 'usd',
            'interval': 'month',
            'interval_count': 1,
            'trial_period_days': 10,
            'statement_descriptor': 'TEAM MONTHLY PLAN',
            'metadata': {
                'recommended': True
            }
        },
        '2': {
            'id': 'Enterprise',
            'name': 'Enterprise',
            'amount': 2400,
            'currency': 'usd',
            'interval': 'month',
            'interval_count': 1,
            'trial_period_days': 5,
            'statement_descriptor': 'ENTERPRISE MONTHLY PLAN'
        }
    }


class Development(Config):
    DEBUG = True
    HOST = '127.0.0.1'
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_PUBLIC_KEY')
    PORT = 5000

class Production(Config):
    DEBUG = False
    HOST = '0.0.0.0'
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_PUBLIC_KEY')
    PORT = 80


config = {
    'dev': Development,
    'prod': Production,
    'default': Development
}
