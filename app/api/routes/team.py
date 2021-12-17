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

team = Namespace('Teams', \
description='This namespace contains team manipulation routes. It requires authentication to access \
    with the `token` sent from the api response which can be found in the `authentication` namespace.', \
path='/team')



@team.doc(security='KEY')
@team.doc(responses={ 200: 'OK successful', 201: 'Creation successful', 301: 'Redirrect', 400: 'Invalid Argument', 401: 'Forbidden Access', 500: 'Mapping Key Error or Internal server error' },
    params= { 'id': 'ID of the site to view heatmap data'})
@team.route('/')
class Team(Resource):
    # get method
    @team.doc(description='This route is to get all or one of the teams from the db. Passing an id will \
        return a particular team with that id else it will return all teams belonging to the user.')
    @team.marshal_with(schema.teamdata)
    @team.vendor(
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

    # post method
    @team.doc(description='This route is to add a new team to the db.')
    @team.expect(schema.putteamdata)
    @team.vendor(
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
            size = postdata['size']
            organization = Organizations.query.filter_by(uuid=postdata['organization_id']).first()
            updated_at = postdata['updated_at'] if 'updated_at' in postdata else None
            if organization:
                team = Teams(name, size, updated_at, user.id, organization.id)
                db.session.add(team)
                db.session.commit()
                return {
                    'result': 'Team saved',
                    'status': True
                }, 200
            else:
                return {
                    'result': 'Invalid organization',
                    'status': False
                }, 200

    # patch method
    @team.doc(description='This route is to update an existing team in the db.')
    @team.expect(schema.teamdata)
    @team.vendor(
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
            id = request.args.get('id')
            name = postdata['name']
            size = postdata['size']
            organization_id = postdata['organization_id']
            updated_at = postdata['updated_at'] if 'updated_at' in postdata else None

            if id:
                team = Teams.query.filter((Teams.uuid == id) & (Teams.user_id == user.id) & (Teams.organizations_id == organization_id)).first()
                if team:
                    team.name = name
                    team.size = size
                    team.updated_at = parser.parse(updated_at)
                    db.session.merge(team)
                    db.session.commit()
                    return {
                        'result': 'team updated',
                        'status': True
                    }, 200
                else:
                    return {
                        'result': 'No team found',
                        'status': False
                    }, 200
            else:
                return {
                    'result': 'No teams found',
                    'status': False
                }, 200
        return {
            'result': 'Invalid data',
            'status': False
        }, 200

    # delete method
    @team.doc(description='This route is to delete an team from the db. Passing an id will \
        delete the particular team with that id else it will return an error.')
    @team.vendor(
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
        id = request.args.get('id')
        token = request.headers['auth-token']
        tokendata = jwt.decode(token, app.config.get('SECRET_KEY'), algorithms=['HS256'])
        user = Users.query.filter_by(uuid=tokendata['uuid']).first()
        if id:
            team = Teams.query.filter((Teams.uuid == id) & (Teams.user_id == user.id)).first()
            db.session.delete(team)
            db.session.commit()
            return {
                'result': 'team removed',
                'status': True
            }, 200
        else:
            return {
                'result': 'No team specified',
                'status': False
            }, 200