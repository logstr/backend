from flask_restplus.inputs import iso8601interval
from app.api import apisec
from flask_restplus import fields



appinfo = apisec.model('Info', {
    'name': fields.String,
    'version': fields.Integer,
    'date': fields.String,
    'author': fields.String,
    'description': fields.String
})

logindata = apisec.model('Login', {
    'username': fields.String(required=True, max_length=64, description='Username of account or business name', example='john'),
    'password': fields.String(required=True, max_length=60, description='User password of the associated username', example='**********')
})

signupdata = apisec.model('Signup', {
    'firstname': fields.String(required=True, max_length=64, description='firstname of account or business name', example='john'),
    'lastname': fields.String(required=True, max_length=64, description='lastname of account or business name', example='Doe'),
    'number': fields.String(required=True, max_length=30, example='+237650221486', \
        description='''User number without verification will send a verification code to user \
            user number with verification will authenticate the user.'''),
    'password': fields.String(required=True, max_length=60, description='User password of the associated username', example='**********'),
    'Team': fields.String(required=True, max_length=30, \
        description='''Team uuid provided by the response of api'''),
    'Organization': fields.String(required=True, max_length=30, \
        description='''Organization uuid provided by api reponse'''),
})