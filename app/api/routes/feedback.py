from functools import wraps
import uuid, json
from flask.ctx import AppContext
from flask_restx import Namespace, Resource
from flask_restx.marshalling import marshal_with, marshal
from app.api import schema
from app import db
from app.models import Users, Projects, Sessions, \
    Organizations, Teams, Heatmaps
from datetime import datetime
from datetime import  timedelta
import jwt
from flask import current_app as app
from flask import request




def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'auth-token' in request.headers:
            token = request.headers['auth-token']
            try:
                data = jwt.decode(token, app.config.get('SECRET_KEY'), algorithms=['HS256'])
            except:
                return {'message': 'Token is invalid.'}, 403
        if not token:
            return {'message': 'Token is missing or not found.'}, 401
        if data:
            pass
        return f(*args, **kwargs)
    return decorated

feedback = Namespace('ML Feedback Analysis', \
description='This namespace contains heatmap manipulation routes. It requires authentication to access \
    with the `token` sent from the api response which can be found in the `authentication` namespace.', \
path='/feedback')



@feedback.doc(security='KEY')
@feedback.doc(responses={ 200: 'OK successful', 201: 'Creation successful', 301: 'Redirrect', 400: 'Invalid Argument', 401: 'Forbidden Access', 500: 'Mapping Key Error or Internal server error' })
@feedback.route('/')
class Feeedback(Resource):
    # get method
    @feedback.doc(description='This route gets all the heatings of a particular session. It isn\'t \
        parginated so this may return a bulky result or may be s little slow to return if data is more \
            than `500` results. If you want a parginated result, see the other get route.',\
            params={'type': 'click'})
    @feedback.marshal_with(schema.getheatdata)
    @token_required
    def get(self):
        type =  request.args.get('type')
        if type:
            heats = Heatmaps.query.filter_by(event_type=type).all()
            return heats, 200
        else:
            return {
                'result': 'No data',
                'status': False
            }, 200

    # Post method
    @feedback.doc(description='This route is to put session heated data into the database')
    @feedback.expect(schema.postrecordingdata)
    @token_required
    def post(self):
        postdata = request.get_json()
        if postdata:
            session_uuid = postdata['session_uuid'] if 'session_uuid' in postdata else None

            session = Sessions.query.filter_by(uuid=session_uuid).first()
            if session:
                session.launch_insert('addheat', postdata, session.id)
                return {
                    'result': 'heatmap saved',
                    'status': True
                }, 200
            else:
                return {
                    'result': 'No session found',
                    'status': False
                }, 200
        return {
            'result': 'Invalid data',
            'status': False
        }, 200
