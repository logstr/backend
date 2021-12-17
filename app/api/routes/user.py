from functools import wraps
from flask_restplus import Namespace, Resource
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
                data = jwt.decode(token, app.config.get('SECRET_KEY'), algorithms=['HS256'])
            except:
                return {'message': 'Token is invalid.'}, 403
        if not token:
            return {'message': 'Token is missing or not found.'}, 401
        if data:
            pass
        return f(*args, **kwargs)
    return decorated

appuser = Namespace('Users', \
description='This namespace contains useranization manipulation routes. It requires authentication to access \
    with the `token` sent from the api response which can be found in the `authentication` namespace.', \
path='/user')



@appuser.doc(security='KEY')
@appuser.doc(responses={ 200: 'OK successful', 201: 'Creation successful', 301: 'Redirrect', 400: 'Invalid Argument', 401: 'Forbidden Access', 500: 'Mapping Key Error or Internal server error' },
    params= { 'id': 'ID of the site to view heatmap data'})
@appuser.route('/')
class Data(Resource):
    # get method
    @appuser.doc(description='This route is to get all or one of the useranizarions from the db. Passing an id will \
        return a particular useranization with that id else it will return all useranizations belonging to the user.')
    @appuser.marshal_with(schema.userdata)
    @appuser.vendor(
        {
            'x-codeSamples':
            [
                { 
                    "lang": "JavaScript",
                    "source": "console.log('Hello World');" 
                },
                { 
                    "lang": "Curl",
                    "source": "curl -X PUT -H "
                }
            ]
        })
    @token_required
    def get(self):
        token = request.headers['auth-token']
        tokendata = jwt.decode(token, app.config.get('SECRET_KEY'), algorithms=['HS256'])
        user = Users.query.filter_by(uuid=tokendata['uuid']).first()
        if user:
            return user, 200
        else:
            return {
                'result': 'No data',
                'status': False
            }, 200

    # patch method
    @appuser.doc(description='This route is to update an existing useranization in the db.')
    @appuser.expect(schema.userdata)
    @appuser.vendor(
        {
            'x-codeSamples':
            [
                { 
                    "lang": "JavaScript",
                    "source": "console.log('Hello World');" 
                },
                { 
                    "lang": "Curl",
                    "source": "curl -X PUT -H "
                }
            ]
        })
    @token_required
    def put(self):
        postdata = request.get_json()
        token = request.headers['auth-token']
        tokendata = jwt.decode(token, app.config.get('SECRET_KEY'), algorithms=['HS256'])
        user = Users.query.filter_by(uuid=tokendata['uuid']).first()
        if postdata:
            first_name = postdata['first_name'] if 'first_name' in postdata else None
            last_name = postdata['last_name'] if 'last_name' in postdata else None
            email = postdata['email'] if 'email' in postdata else None
            number = postdata['number'] if 'number' in postdata else None

            if user:
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.number = number
                db.session.merge(user)
                db.session.commit()
                return {
                    'result': 'user updated',
                    'status': True
                }, 200
            else:
                return {
                    'result': 'No user found',
                    'status': False
                }, 200
        return {
            'result': 'Invalid data',
            'status': False
        }, 200

    # delete method
    @appuser.doc(description='This route is to delete an useranization from the db. Passing an id will \
        delete the particular useranization with that id else it will return an error.')
    @appuser.vendor(
        {
            'x-codeSamples':
            [
                { 
                    "lang": "JavaScript",
                    "source": "console.log('Hello World');" 
                },
                { 
                    "lang": "Curl",
                    "source": "curl -X PUT -H "
                }
            ]
        })
    @token_required
    def delete(self):
        token = request.headers['auth-token']
        tokendata = jwt.decode(token, app.config.get('SECRET_KEY'), algorithms=['HS256'])
        user = Users.query.filter_by(uuid=tokendata['uuid']).first()
        if user:
            db.session.commit()
            return {
                'result': 'user removed',
                'status': True
            }, 200
        else:
            return {
                'result': 'No user specified',
                'status': False
            }, 200