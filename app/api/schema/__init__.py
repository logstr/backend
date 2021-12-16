from flask_restplus.inputs import iso8601interval
from app.api import apisec
from flask_restplus import fields



appinfo = apisec.model('Info', {
    'name': fields.String,
    'version': fields.Integer,
    'date': fields.String,
    'author': fields.String,
    'description': fields.String
})

logindata = apisec.model('Login', {
    'firstname': fields.String(required=True, max_length=64, description='Username of account or business name', example='john'),
    'password': fields.String(required=True, max_length=60, description='User password of the associated username', example='**********')
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

sessiondata = apisec.model('Sessiondata', {
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
    'ip': fields.String(required=True, max_length=64, description='IP address of the session', example='154.0.0.24'),
    'device': fields.String(required=True, max_length=60, description='Platform on which the project is suppose to run'),
    'startTime': fields.DateTime(),
    'endTime': fields.DateTime(),
    'project': fields.String(required=True, max_length=30, description='Project name provided by api reponse'),
    'project_id': fields.String(required=True, max_length=60, description='Project uuid provided by api reponse'),
    'navigator': fields.String(required=True, max_length=300, description='Organization uuid provided by api reponse'),
    'team_id': fields.String(required=True, max_length=60, description='uuid of the Team who owns the project'),
})

projectdata = apisec.model('Projectdata', {
    'name': fields.String(required=True, max_length=64, description='Name of business or organization', example='project-x'),
    'platform': fields.String(required=True, max_length=60, description='Platform on which the project is suppose to run'),
    'team_id': fields.String(required=True, max_length=60, description='uuid of the Team who owns the project'),
    'organization_id': fields.String(required=True, max_length=60, description='Organization uuid provided by api reponse'),
    'updated_at': fields.DateTime()
})

teamdata = apisec.model('Teamdata', {
    'uuid': fields.String(max_length=60, description='object if of the team'),
    'name': fields.String(required=True, max_length=64, description='Name of business or organization', example='A-Team'),
    'size': fields.Integer,
    'user_id': fields.String(max_length=30, description='Owner or creator of the team.'),
    'organization_id': fields.String(max_length=60, description='Organization uuid provided by api reponse'),
    'updated_at': fields.DateTime()
})

organizationdata = apisec.model('Organizationdata', {
    'uuid': fields.String(max_length=60, description='object if of the organization'),
    'name': fields.String(required=True, max_length=64, description='Name of business or organization', example='Acmecorp'),
    'updated_at': fields.DateTime()
})