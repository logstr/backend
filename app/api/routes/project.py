from functools import wraps
import uuid
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

project = Namespace('Project', \
description='This namespace contains team manipulation routes. It requires authentication to access \
    with the `token` sent from the api response which can be found in the `authentication` namespace.', \
path='/project')



@project.doc(security='KEY')
@project.doc(responses={ 200: 'OK successful', 201: 'Creation successful', 301: 'Redirrect', 400: 'Invalid Argument', 401: 'Forbidden Access', 500: 'Mapping Key Error or Internal server error' },
    params= { 
        'id': 'uuid of the project', 
        'team' : 'Team uuid'
    })
@project.route('/')
class Project(Resource):
    # get method
    @project.doc(description='This route is to get all or one of the teams from the db. Passing an id will \
        return a particular team with that id else it will return all teams belonging to the user.')
    @project.marshal_with(schema.projectdata)
    @project.vendor(
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
        id = request.args.get('id')
        team = Teams.query.filter_by(uuid=request.args.get('team')).first()
        if team:
            if id:
                teamproject = Teams.query.filter((Teams.uuid==team.uuid) & (Teams.user_id==user.id)).first()
                project = Projects.query.filter((Projects.teams_id==teamproject.id) & (Projects.uuid==id)).first()
                return project, 200
            else:
                teamproject =  Teams.query.filter((Teams.uuid==team.uuid) & (Teams.user_id==user.id)).first()
                project = Projects.query.filter_by(teams_id=teamproject.id).all()
                return project, 200
        else:
           return {
                'result': 'Invalid data',
                'status': False
            }, 200 

    # post method
    @project.doc(description='This route is to add a new team to the db.')
    @project.expect(schema.putprojectdata)
    @project.vendor(
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
    @project.doc(description='This route is to update an existing team in the db.')
    @project.expect(schema.patchprojectdata)
    @project.vendor(
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
            id = postdata['uuid']
            name = postdata['name']
            platform = postdata['platform']

            if id:
                userteams = Teams.query.filter_by(user_id=user.id).all()
                for team in userteams:
                    teamproject = Projects.query.filter((Projects.uuid==id) & (Projects.teams_id==team.id)).first()
                    if teamproject:
                        teamproject.name = name
                        teamproject.platform = platform
                        db.session.merge(teamproject)
                        db.session.commit()
                        return {
                            'result': 'Project updated',
                            'status': True
                        }, 200
                else:
                    return {
                        'result': 'No Project found',
                        'status': False
                    }, 200
            else:
                return {
                    'result': 'No Project found',
                    'status': False
                }, 200
        return {
            'result': 'Invalid data',
            'status': False
        }, 200

    # delete method
    @project.doc(description='This route is to delete an team from the db. Passing an id will \
        delete the particular team with that id else it will return an error.')
    @project.vendor(
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
            userteams = Teams.query.filter_by(user_id=user.id).all()
            for team in userteams:
                teamproject = Projects.query.filter((Projects.uuid==id) & (Projects.teams_id==team.id)).first()
                if teamproject:
                    db.session.delete(teamproject)
                    db.session.commit()
                    return {
                        'result': 'Project removed',
                        'status': True
                    }, 200
                else:
                    return {
                        'result': 'No Project found',
                        'status': False
                    }, 200
        else:
            return {
                'result': 'No project specified',
                'status': False
            }, 200