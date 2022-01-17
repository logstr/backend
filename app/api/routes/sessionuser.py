from functools import wraps
import uuid
from flask_restx import Namespace, Resource
from app.api import schema
from app import db
from app.models import Users, Projects, Sessions, \
    Organizations, Teams, Heatmaps, Sessionuser as SessionuserModel
from datetime import datetime
from datetime import  timedelta
import jwt
from flask import current_app as app
from flask import request
from dateutil import parser
from sqlalchemy.sql.operators import Operators


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

sessionuser = Namespace('Sessionusers', \
description='This namespace contains usersession manipulation routes. It `DOES NOT` requires authentication traditionally to access. \
   Although some routes may need', \
path='/sessionuser')



@sessionuser.doc(security='KEY')
@sessionuser.doc(responses={ 200: 'OK successful', 201: 'Creation successful', 301: 'Redirrect', 400: 'Invalid Argument', 401: 'Forbidden Access', 500: 'Mapping Key Error or Internal server error' })
@sessionuser.route('/')
class Sessionuser(Resource):
    # get method
    @sessionuser.doc(description='This route is to get all or one of the useranizarions from the db. Passing an id will \
        return a particular useranization with that id else it will return all useranizations belonging to the user.', \
            params= { 'id': 'ID of the project', 'uuid':'ID of the sessionuser'})
    @sessionuser.marshal_with(schema.sessionuser)
    @token_required
    def get(self):
        token = request.headers['auth-token']
        project_id = request.args.get('id')
        uuid = request.args.get('uuid')
        tokendata = jwt.decode(token, app.config.get('SECRET_KEY'), algorithms=['HS256'])
        user = Users.query.filter_by(uuid=tokendata['uuid']).first()
        if user:
            project = Projects.query.filter_by(uuid=project_id).first()
            if project:
                projectorg = db.session.query(Organizations) \
                    .join(Projects).filter((Organizations.id == project.organizations_id) \
                        & (Organizations.user_id == user.id)).all()

                if projectorg:
                    if uuid:
                        sessions = SessionuserModel.query.filter_by(uuid=uuid).first()
                        return sessions, 200
                    else:
                        sessions = SessionuserModel.query.all()
                        return sessions, 200
                else:
                    return {
                        'result': 'No data',
                        'status': False
                    }, 200
            else:
                return {
                    'result': 'No data',
                    'status': False
                }, 200
        else:
            return {
                'result': 'No data',
                'status': False
            }, 200


    # post method
    @sessionuser.doc(description='This route is to update an existing useranization in the db.')
    @sessionuser.expect(schema.sessionuser)
    def post(self):
        postdata = request.get_json()

        if postdata:
            username = postdata['name'] if 'name' in postdata else None
            email = postdata['email'] if 'email' in postdata else None
            project_id = postdata['project_id'] if 'project_id' in postdata else None

            project = Projects.query.filter_by(uuid=project_id).first()
            # create a session or append one
            if project:
                newsessionuser = SessionuserModel(username, email, project.id)
                db.session.add(newsessionuser)
                db.session.commit()
                return {
                    'result': 'created user',
                    'data': newsessionuser.uuid,
                    'status': True
                }, 200
            else:
                return {
                    'result': 'no project found',
                    'status': False
                }, 200
        return {
            'result': 'Invalid data',
            'status': False
        }, 200

    @sessionuser.doc(description='This route is to get all or one of the useranizarions from the db. Passing an id will \
        return a particular useranization with that id else it will return all useranizations belonging to the user.', \
            params= { 'id': 'ID of the sessionuser', 'uuid': 'ID of the user to delete'})
    @token_required
    def delete(self):
        token = request.headers['auth-token']
        project_id = request.args.get('id')
        uuid = request.args.get('uuid')
        tokendata = jwt.decode(token, app.config.get('SECRET_KEY'), algorithms=['HS256'])
        user = Users.query.filter_by(uuid=tokendata['uuid']).first()
        if user:
            project = Projects.query.filter_by(uuid=project_id).first()
            if project:
                projectorg = db.session.query(Organizations) \
                    .join(Projects).filter((Organizations.id == project.organizations_id) \
                        & (Organizations.user_id == user.id)).all()

                if projectorg:
                    session = SessionuserModel.query.filter_by(uuid=uuid).first()
                    db.session.delete(session)
                    db.session.commit()
                    return {
                        'result': 'User Deleted',
                        'status': False
                    }, 200
                else:
                    return {
                        'result': 'No data',
                        'status': False
                    }, 200
            else:
                return {
                    'result': 'No data',
                    'status': False
                }, 200
        else:
            return {
                'result': 'No data',
                'status': False
            }, 200