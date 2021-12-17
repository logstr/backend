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

org = Namespace('Organization', \
description='This namespace contains organization manipulation routes. It requires authentication to access \
    with the `token` sent from the api response which can be found in the `authentication` namespace.', \
path='/org')



@org.doc(security='KEY')
@org.doc(responses={ 200: 'OK successful', 201: 'Creation successful', 301: 'Redirrect', 400: 'Invalid Argument', 401: 'Forbidden Access', 500: 'Mapping Key Error or Internal server error' },
    params= { 'id': 'ID of the site to view heatmap data'})
@org.route('/')
class Organization(Resource):
    # get method
    @org.doc(description='This route is to get all or one of the organizarions from the db. Passing an id will \
        return a particular organization with that id else it will return all organizations belonging to the user.')
    @org.marshal_with(schema.organizationdata)
    @org.vendor(
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
            organization = user.organizations.query.filter_by(uuid=id).first()
            return organization, 200
        else:
            organization = user.organizations.all()
            return organization, 200

    # post method
    @org.doc(description='This route is to add a new organization to the db.')
    @org.expect(schema.organizationdata)
    @org.vendor(
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
            name= postdata['name']
            updated_at = postdata['updated_at'] if 'updated_at' in postdata else None

            org = Organizations(name, updated_at, user.id)
            db.session.add(org)
            db.session.commit()
            return {
                'result': 'organization saved',
                'status': True
            }, 200

    # patch method
    @org.doc(description='This route is to update an existing organization in the db.')
    @org.expect(schema.organizationdata)
    @org.vendor(
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
            uuid = postdata['uuid']
            name= postdata['name']
            updated_at = postdata['updated_at'] if 'updated_at' in postdata else None

            if uuid:
                organization = Organizations.query.filter((Organizations.uuid == uuid) & (Organizations.user_id == user.id)).first()
                organization.name = name
                organization.updated_at = parser.parse(updated_at)
                db.session.merge(organization)
                db.session.commit()
                return {
                    'result': 'Organization updated',
                    'status': True
                }, 200
            else:
                return {
                    'result': 'No organizations found',
                    'status': False
                }, 200
        return {
            'result': 'Invalid data',
            'status': False
        }, 200

    # delete method
    @org.doc(description='This route is to delete an organization from the db. Passing an id will \
        delete the particular organization with that id else it will return an error.')
    @org.vendor(
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
            organization = Organizations.query.filter((Organizations.uuid == id) & (Organizations.user_id == user.id)).first()
            db.session.delete(organization)
            db.session.commit()
            return {
                'result': 'Organization removed',
                'status': True
            }, 200
        else:
            return {
                'result': 'No organization specified',
                'status': False
            }, 200