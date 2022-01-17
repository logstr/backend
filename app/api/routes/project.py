from functools import wraps
import uuid
from flask_restx import Namespace, Resource
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

project = Namespace('Projects', \
description='This namespace contains team manipulation routes. It requires authentication to access \
    with the `token` sent from the api response which can be found in the `authentication` namespace.', \
path='/project')



@project.doc(security='KEY')
@project.doc(responses={ 200: 'OK successful', 201: 'Creation successful', 301: 'Redirrect', 400: 'Invalid Argument', 401: 'Forbidden Access', 500: 'Mapping Key Error or Internal server error' })
@project.route('/')
class Project(Resource):
    # get method
    @project.doc(description='This route is to get all or one of the teams from the db. Passing an id will \
        return a particular team with that id else it will return all teams belonging to the user.',
        params= { 
        'id': 'uuid of the project', 
        'org' : 'Organization uuid'
    })
    @project.marshal_with(schema.projectdata)
    @token_required
    def get(self):
        token = request.headers['auth-token']
        tokendata = jwt.decode(token, app.config.get('SECRET_KEY'), algorithms=['HS256'])
        user = Users.query.filter_by(uuid=tokendata['uuid']).first()
        id = request.args.get('id')
        organ = Organizations.query.filter_by(uuid=request.args.get('org')).first()
        if organ:
            orgproject = Organizations.query.filter((Organizations.uuid==organ.uuid) & (Organizations.user_id==user.id)).first()
            if id:
                project = Projects.query.filter_by(uuid=id).first()
                return project, 200
            else:
                project = Projects.query.filter_by(organizations_id=orgproject.id).all()
                return project, 200
        else:
           return {
                'result': 'Invalid data',
                'status': False
            }, 200 

    # post method
    @project.doc(description='This route is to add a new team to the db.')
    @project.expect(schema.putprojectdata)
    @token_required
    def post(self):
        postdata = request.get_json() 
        token = request.headers['auth-token']
        tokendata = jwt.decode(token, app.config.get('SECRET_KEY'), algorithms=['HS256'])
        user = Users.query.filter_by(uuid=tokendata['uuid']).first()
        if postdata:
            name = postdata['name']
            platform = postdata['platform'] if 'platform' in postdata else None
            organ = postdata['organizations_id'] if 'organizations_id' in postdata else None
            organization = Organizations.query.filter((Organizations.uuid == organ) & (Organizations.user_id == user.id)).first()
            if organization:
                exproject = Projects.query.filter_by(name=name).first()
                if exproject is None:
                    project = Projects(name, platform, user.id, organization.id)
                    db.session.add(project)
                    db.session.commit()
                    return {
                        'result': 'Project saved',
                        'status': True
                    }, 200
                else:
                    return {
                        'result': 'Project already exist',
                        'status': False
                    }, 200
            else:
                return {
                    'result': 'Invalid Team or organization',
                    'status': False
                }, 200

    # patch method
    @project.doc(description='This route is to update an existing team in the db.')
    @project.expect(schema.patchprojectdata)
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
                teamproject = Projects.query.filter((Projects.uuid==id) & \
                    (Projects.admin==user.uuid) & \
                        (Projects.name==name)).first()
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
        return {
            'result': 'Invalid data',
            'status': False
        }, 200

    # delete method
    @project.doc(description='This route is to delete an team from the db. Passing an id will \
        delete the particular team with that id else it will return an error.',
        params= { 
        'id': 'uuid of the project', 
        'org' : 'Organization uuid'
    })
    @token_required
    def delete(self):
        id = request.args.get('id')
        orgs = request.args.get('org')
        token = request.headers['auth-token']
        tokendata = jwt.decode(token, app.config.get('SECRET_KEY'), algorithms=['HS256'])
        user = Users.query.filter_by(uuid=tokendata['uuid']).first()
        if id:
            userorganizations = Organizations.query.filter_by(uuid=orgs).first()
            if userorganizations:
                orgproject = Projects.query.filter((Projects.uuid==id) & \
                    (Projects.organizations_id==userorganizations.id) & \
                        (Projects.admin==user.id)).first()
                if orgproject:
                    db.session.delete(orgproject)
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