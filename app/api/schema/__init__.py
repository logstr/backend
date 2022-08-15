from os import name
import uuid
from flask_restx.inputs import iso8601interval
from app.api import apisec
from flask_restx import fields
from app import ma
from app.models import Users


class UsersSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Users


appinfo = apisec.model('Info', {
    'name': fields.String,
    'version': fields.String,
    'date': fields.String,
    'author': fields.String,
    'description': fields.String
})

logindata = apisec.model('Login', {
    'email': fields.String(required=True, max_length=64, description='Email of account or business name', example='john@acme.org'),
    'password': fields.String(required=True, max_length=60, description='User password of the associated username', example='**********')
})

resetdata = apisec.model('Reset', {
    'email': fields.String(required=True, max_length=64, description='Email of account or business name', example='john@acme.org'),
    'password': fields.String(required=True, max_length=60, description='User password of the associated username', example='**********'),
    'token': fields.String(required=True, description='`token` sent to email', example='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.ey...')
})

signupdata = apisec.model('Signup', {
    'firstname': fields.String(required=True, max_length=64, description='firstname of account or business name', example='john'),
    'lastname': fields.String(required=True, max_length=64, description='lastname of account or business name', example='doe'),
    'email': fields.String(max_length=64, description='user email associated for verification e.g john@acme.org', example='john@acme.org'),
    'number': fields.String(max_length=30, example='+237650221486', \
        description='''User number without verification will send a verification code to user \
            user number with verification will authenticate the user.'''),
    'password': fields.String(required=True, max_length=60, description='User password of the associated username', example='**********')
})

userdata = apisec.model('User', {
    'first_name': fields.String(required=True, max_length=64, description='firstname of account or business name', example='john'),
    'last_name': fields.String(required=True, max_length=64, description='lastname of account or business name', example='doe'),
    'emailaddress': fields.String(max_length=64, description='user email associated for verification e.g john@acme.org', example='john@acme.org'),
    'phone': fields.String(max_length=30, example='+237650221486', \
        description='''User number without verification will send a verification code to user \
            user number with verification will authenticate the user.''')
})

usersessiondata = apisec.model('Usersessiondata', {
    'username': fields.String(max_length=64, description='username app user or reoccuring visitor', example='adam'),
    'emailaddress': fields.String(max_length=64, description='email associated with reoccuring user e.g adam@acme.org', example='adam@acme.org'),
    'sessionid': fields.String(max_length=64, description='`id` of the session', example='2467'),
    'sessionuuid': fields.String(max_length=64, description='`uuid` of the session', example='769732655d06491d9792cf1d7f3aea2c')
})

getheatdata = apisec.model('getheatdata', {
    'x': fields.Integer,
    'y': fields.Integer,
    'value': fields.Integer
})

putheatdata = apisec.model('Sessiondata', {
    'username': fields.String(max_length=64, description='username app user or reoccuring visitor', example='adam'),
    'emailaddress': fields.String(max_length=64, description='email associated with reoccuring user e.g adam@acme.org', example='adam@acme.org'),
    'ip': fields.String(required=True, max_length=64, description='IP address of the session', example='154.0.0.24'),
    'xdata': fields.Integer,
    'ydata': fields.Integer,
    'value': fields.Integer,
    'event_type_key': fields.String(default='click', enum=['click', 'move', 'scroll'], description='Type of event'),
    'event': fields.String(required=True, max_length=60, description='Event name'),
    'session_uuid': fields.String(required=True, max_length=60, description='Session uuid of the project'),
    'timestamp': fields.DateTime(),
    'event_info': fields.String(required=True, max_length=300, description='Organization uuid provided by api reponse')
})

sessiondata = apisec.model('Sessiondata', {
    'username': fields.String(max_length=64, description='username app user or reoccuring visitor', example='adam'),
    'emailaddress': fields.String(max_length=64, description='email associated with reoccuring user e.g adam@acme.org', example='adam@acme.org'),
    'ip': fields.String(required=True, max_length=64, description='IP address of the session', example='154.0.0.24'),
    'device': fields.String(required=True, max_length=64, description='Device name', example='Mac Os'),
    'project_id': fields.String(required=True, max_length=60, description='uuid of the project', example='769732655d06491d9792cf1d7f3aea2c'),
    'navigator': fields.String(required=True, max_length=64, description='Navigator information of the session', example='{\'navigator\': \'xxxx\'}'),
    'startTime': fields.DateTime(),
    'endTime': fields.DateTime()
})
getsessiondata = apisec.model('Getsessiondata', {
    'ip_address': fields.String(required=True, max_length=64, description='IP address of the session', example='154.0.0.24'),
    'device': fields.String(required=True, max_length=64, description='Device name', example='Mac Os'),
    'projects_id': fields.Integer,
    'sessions_user_id': fields.Integer,
    'navigator_info': fields.String(required=True, max_length=64, description='Navigator information of the session', example='{\'navigator\': \'xxxx\'}'),
    'start_time': fields.DateTime(),
    'end_time': fields.DateTime(),
    'created_at': fields.DateTime()
})

getrecordingdata = apisec.model('getrecordingdata', {
    'data': fields.Raw(),
    'type': fields.Integer(description='Type of mutation', example=3),
    'timestamp': fields.Integer
})

postrecordingdata = apisec.model('postrecordingdata', {
    'session_uuid': fields.String(required=True, description='Id of the session', example='769732655d06491d9792cf1d7f3aea2c'),
    'recdata': fields.String()
})

sessionuser = apisec.model('Sessionuser', {
    'name': fields.String(max_length=64, description='username app user or reoccuring visitor', example='adam'),
    'email': fields.String(max_length=64, description='email associated with reoccuring user e.g adam@acme.org', example='adam@acme.org'),
    'projects_id': fields.String(required=True, max_length=60, description='uuid of the project', example='769732655d06491d9792cf1d7f3aea2c'),
})

putprojectdata = apisec.model('Putprojectdata', {
    'name': fields.String(required=True, max_length=64, description='Name of business or organization', example='project-x'),
    'platform': fields.String(required=True, max_length=60, description='Platform on which the project is suppose to run'),
    'organizations_id': fields.String(required=True, max_length=60, description='Organization uuid provided by api reponse')
})

patchprojectdata = apisec.model('Patchprojectdata', {
    'uuid': fields.String(max_length=60, description='object id of the project'),
    'name': fields.String(required=True, max_length=64, description='Name of business or organization', example='project-x'),
    'platform': fields.String(required=True, max_length=60, description='Platform on which the project is suppose to run')
})

projectdata = apisec.model('Projectdata', {
    'uuid': fields.String(max_length=60, description='object id of the project'),
    'name': fields.String(required=True, max_length=64, description='Name of business or organization', example='project-x'),
    'platform': fields.String(max_length=60, description='Platform on which the project is suppose to run'),
    'organizations_id': fields.String(required=True, max_length=60, description='Organization uuid provided by api reponse')
})

putteamdata = apisec.model('Putteamdata', {
    'name': fields.String(required=True, max_length=64, description='Name of business or organization', example='A-Team'),
    'size': fields.Integer,
    'organization_id': fields.String(max_length=60, description='Organization uuid provided by api reponse'),
    'updated_at': fields.DateTime()
})

teamdata = apisec.model('Teamdata', {
    'uuid': fields.String(max_length=60, description='object if of the team'),
    'name': fields.String(required=True, max_length=64, description='Name of business or organization', example='A-Team'),
    'size': fields.Integer,
    'user_id': fields.String(max_length=30, description='Owner or creator of the team.'),
    'organizations_id': fields.String(max_length=60, description='Organization uuid provided by api reponse'),
    'updated_at': fields.DateTime()
})

putorganizationdata = apisec.model('putOrganizationdata', {
    'uuid': fields.String(max_length=60, description='object if of the organization'),
    'name': fields.String(required=True, max_length=64, description='Name of business or organization', example='Acmecorp'),
    'updated_at': fields.DateTime()
})

getorganizationdata = apisec.model('getOrganizationdata', {
    'uuid': fields.String(max_length=60, description='object if of the organization'),
    'name': fields.String(required=True, max_length=64, description='Name of business or organization', example='Acmecorp'),
    'updated_at': fields.DateTime()
})

postorganizationdata = apisec.model('postOrganizationdata', {
    'name': fields.String(required=True, max_length=64, description='Name of business or organization', example='Acmecorp'),
    'updated_at': fields.DateTime()
})
returnsessionuser = apisec.model('returnsessionuser', {
    'uuid': fields.String(required=True, max_length=64, description='Name of business or organization', example='iosfjnjbkamdfjjsfjk'),
    'name': fields.String(required=True, max_length=64, description='Name of business or organization', example='iosfjnjbkamdfjjsfjk'),
    'email': fields.String(required=True, max_length=64, description='Name of business or organization', example='iosfjnjbkamdfjjsfjk')
})

returnsession = apisec.model('returnsession', {
    'uuid': fields.String(required=True, max_length=64, description='Name of business or organization', example='iosfjnjbkamdfjjsfjk'),
    'ip_address': fields.String(required=True, max_length=64, description='Name of business or organization', example='192.0.0.1'),
    'projects_id': fields.String(required=True, max_length=64, description='Name of business or organization', example='hskdhfakdhfoiwerknlj'),
    'session_user': fields.Nested(returnsessionuser)
})
