from functools import wraps
import uuid, json
from flask_restx import Namespace, Resource
from flask_restx.marshalling import marshal_with, marshal
from app.api import schema
from app import db
from app.models import Users, Projects, Sessions, \
    Organizations, Teams, Heatmaps, Recordings
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
                data = jwt.decode(token, app.config.get('SECRET_KEY'), algorithms=['HS256'])
            except:
                return {'message': 'Token is invalid.'}, 403
        if not token:
            return {'message': 'Token is missing or not found.'}, 401
        if data:
            pass
        return f(*args, **kwargs)
    return decorated

record = Namespace('Recordings', \
description='This namespace contains records manipulation routes. It requires authentication to access \
    with the `token` sent from the api response which can be found in the `authentication` namespace.', \
path='/record')



@record.doc(security='KEY')
@record.doc(responses={ 200: 'OK successful', 201: 'Creation successful', 301: 'Redirrect', 400: 'Invalid Argument', 401: 'Forbidden Access', 500: 'Mapping Key Error or Internal server error' })
@record.route('/')
class Record(Resource):
    # get method
    @record.doc(description='This route gets all the recordings of a particular session. It isn\'t \
        parginated so this may return a bulky result or may be s little slow to return if data is more \
            than `500` results. If you want a parginated result, see the other get route.',\
            params={'session_id':'Session id'})
    @record.marshal_with(schema.getrecordingdata)
    @token_required
    def get(self):
        session_id = request.args.get('session_id')
        session = Sessions.query.filter_by(uuid=session_id).first()
        if session:
            records = Recordings.query.filter_by(sessions_id=session.id).all()
            return records, 200
        else:
            return {
                'result': 'No data',
                'status': False
            }, 200

    # Post method
    @record.doc(description='This route is to put session recorded data into the database')
    @record.expect(schema.postrecordingdata)
    @token_required
    def post(self):
        postdata = request.get_json()
        token = request.headers['auth-token']
        tokendata = jwt.decode(token, app.config.get('SECRET_KEY'), algorithms=['HS256'])
        user = Users.query.filter_by(uuid=tokendata['uuid']).first()
        if postdata:
            session_uuid = postdata['session_uuid'] if 'session_uuid' in postdata else None

            session = Sessions.query.filter_by(uuid=session_uuid).first()
            if session:
                db.session.bulk_save_objects(
                    [
                        Recordings(type=i['type'], \
                            data=i['data'], \
                                timestamp=i['timestamp'], \
                                    session_id=session.id)
                        for i in json.loads(postdata['recdata'])['recordings']
                    ]
                )
                db.session.commit()
                return {
                    'result': 'recording saved',
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

@record.doc(security='KEY')
@record.doc(responses={ 200: 'OK successful', 201: 'Creation successful', 301: 'Redirrect', 400: 'Invalid Argument', 401: 'Forbidden Access', 500: 'Mapping Key Error or Internal server error' },
    params= { 'id': 'ID of the site to record heatmap data'})
@record.route('/user')
class Sessionrecord(Resource):

    @record.doc(description='This route returns a parginated result. It may return faster and it is \
        `recommended` use this route to parginate.',\
            params={'session_id':'Session id', 'start': 'Page of items', 'count':'Number of items to process'})
    @token_required
    def get(self):
        session_id = request.args.get('session_id')
        start  = request.args.get('start', None)
        count = request.args.get('count', None)
        next = "/api/record/user?id="+str(session_id)+"&start="+str(int(start)+1)+"&count="+count
        previous = "/api/record/user?id="+str(session_id)+"&start="+str(int(start)-1)+"&count="+count

        session = Sessions.query.filter_by(uuid=session_id).first()
        if session:
            records = Recordings.query.filter_by(sessions_id=session.id).paginate(int(start), int(count), False).items
            return {
                'data': marshal(records, schema.getrecordingdata),
                'next': next,
                'previous': previous
            }, 200
        else:
            return {
                'result': 'No data',
                'status': False
            }, 200