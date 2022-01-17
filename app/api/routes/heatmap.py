from functools import wraps
from flask_restx import Namespace, Resource, fields
from app.api import schema
from app import db
from app.models import Users, Projects, Sessions, Organizations, Teams, Heatmaps
from datetime import datetime
from datetime import  timedelta
import jwt
from flask import current_app as app
from flask import request
from dateutil import parser
from sqlalchemy.orm.attributes import flag_modified


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'auth-token' in request.headers:
            token = request.headers['auth-token']
            try:
                data = jwt.decode(token, app.config.get('SECRET_KEY'))
            except:
                return {'message': 'Token is invalid.'}, 403
        if not token:
            return {'message': 'Token is missing or not found.'}, 401
        if data:
            pass
        return f(*args, **kwargs)
    return decorated

heat = Namespace('Heatmaps', \
description='This contains data for the **user** and content belonging to the \
application to be shared. The android and iOS application will make calls from \
these endpoints. Tokens will be the method of security with two tokens, a  \
refresh `token` ( **30 days span** ) and a normal token ( **7 days** ) ', \
path='/heatmap')



@heat.doc(security='KEY')
@heat.doc(responses={ 200: 'OK successful', 201: 'Creation successful', 301: 'Redirrect', 400: 'Invalid Argument', 401: 'Forbidden Access', 500: 'Mapping Key Error or Internal server error' },
    params= { 'id': 'ID of the site to view heatmap data'})
@heat.route('/view/<id>')
class View(Resource):
    @heat.doc(description='User enter their `number` and a `code` is sent via **sms** to that number. If an accoutn exist \
        for that number, the code is then heatenticated and if successfull the user proceeds to dashboard.')
    #@heat.marshal_with(schema.heatmapdata)
    @token_required
    def get(self, id):
        return {
            'result': 'Not found',
            'status': 0
        }, 401

@heat.doc(security='KEY')
@heat.doc(responses={ 200: 'OK successful', 201: 'Creation successful', 301: 'Redirrect', 400: 'Invalid Argument', 401: 'Forbidden Access', 500: 'Mapping Key Error or Internal server error' },
    params= { 'id': 'Specify the Id associated with the person' , 
    'name': 'Specify the name associated with the person' }
    )
@heat.route('/add')
class AddData(Resource):
    @heat.doc(description='Data is sent to the server under a particular client IP or Device \
        this data is stored under a particular master site and can be accessed by site owner when they login. \
            this data will then be stored in the heatmap section of the particular site.')
    #@heat.expect(schema.heatmapclient)
    def post(self):
        heatmapdata = request.get_json()
        username = heatmapdata['username']
        site = heatmapdata['site']
        uuid = heatmapdata['uuid']
        ip_add = heatmapdata['ip_add']
        device = heatmapdata['device']
        app = heatmapdata['application']
        agent = heatmapdata['user_agent']
        lang = heatmapdata['language']
        host = heatmapdata['host']
        ref = heatmapdata['referer']
        raw = heatmapdata['raw']
        data = heatmapdata['data']

        return {
            'result': 'Invalid Data',
            'status': 0
        }, 400
