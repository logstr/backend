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