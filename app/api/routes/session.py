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

session = Namespace('Sessions', \
description='This namespace contains useranization manipulation routes. It requires authentication to access \
    with the `token` sent from the api response which can be found in the `authentication` namespace.', \
path='/session')



@session.doc(security='KEY')
@session.doc(responses={ 200: 'OK successful', 201: 'Creation successful', 301: 'Redirrect', 400: 'Invalid Argument', 401: 'Forbidden Access', 500: 'Mapping Key Error or Internal server error' },
    params= { 'id': 'ID of the site to view heatmap data'})
@session.route('/')
class Session(Resource):
    # get method
    @session.doc(description='This route is to get all or one of the useranizarions from the db. Passing an id will \
        return a particular useranization with that id else it will return all useranizations belonging to the user.')
    @session.marshal_with(schema.userdata)
    @session.vendor(
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

    # post method
    @session.doc(description='This route is to add a new team to the db.')
    @session.expect(schema.putprojectdata)
    @session.vendor(
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
    def post(self):
        postdata = request.get_json() 
        token = request.headers['auth-token']
        tokendata = jwt.decode(token, app.config.get('SECRET_KEY'), algorithms=['HS256'])
        user = Users.query.filter_by(uuid=tokendata['uuid']).first()
        if postdata:
            name = postdata['name']
            platform = postdata['platform'] if 'platform' in postdata else None
            team = Teams.query.filter_by(uuid=postdata['team_id']).first()
            organization = Organizations.query.filter((Organizations.uuid == postdata['organization_id']) & (Organizations.user_id == user.id)).first()
            if team:
                project = Projects(name, platform, team_id=team.id, organization_id=organization.id)
                db.session.add(project)
                db.session.commit()
                return {
                    'result': 'Project saved',
                    'status': True
                }, 200
            else:
                return {
                    'result': 'Invalid Team or organization',
                    'status': False
                }, 200

    # patch method
    @session.doc(description='This route is to update an existing useranization in the db.')
    @session.expect(schema.userdata)
    @session.vendor(
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
            email = postdata['emailaddress'] if 'emailaddress' in postdata else None
            number = postdata['phone'] if 'phone' in postdata else None

            if user:
                user.first_name = first_name
                user.last_name = last_name
                user.emailaddress = email
                user.phone = number
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
    @session.doc(description='This route is to delete an useranization from the db. Passing an id will \
        delete the particular useranization with that id else it will return an error.')
    @session.vendor(
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


@session.doc(security='KEY')
@session.doc(responses={ 200: 'OK successful', 201: 'Creation successful', 301: 'Redirrect', 400: 'Invalid Argument', 401: 'Forbidden Access', 500: 'Mapping Key Error or Internal server error' },
    params= { 'id': 'ID of the site to view heatmap data'})
@session.route('/session/project')
class Sessionproject(Resource):

    @session.doc(description='This route is to get all or one of the teams from the db. Passing an id will \
        return a particular team with that id else it will return all teams belonging to the user.')
    @session.marshal_with(schema.teamdata)
    @session.vendor(
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
        id = request.args.get('id')
        token = request.headers['auth-token']
        tokendata = jwt.decode(token, app.config.get('SECRET_KEY'), algorithms=['HS256'])
        user = Users.query.filter_by(uuid=tokendata['uuid']).first()
        if id:
            team = user.teams.query.filter_by(uuid=id).first()
            return team, 200
        else:
            team = user.teams.all()
            return team, 200