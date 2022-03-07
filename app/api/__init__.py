'''
Api related resources
'''

from datetime import datetime
import app
from flask import Blueprint, current_app
from flask_restx import Api, Resource
from flask import Blueprint, render_template, request
from flask_cors import CORS
from functools import wraps
from app import db, sio
from werkzeug.datastructures import FileStorage
from flask_socketio import emit
import jwt


# API security
security={'OAuth2': ['read', 'write']},
authorizations={
    'Google': {
        'type': 'oauth2',
        'flow': 'Authorization Code',
        'authorizationUrl': 'http://localhost:5000/login/authorized',
        'clientId': app.config.get('GOOGLE_CLIENT_ID'),
        'scopes': {
            'email': 'Get user information',
            'profile': 'Get full user identity',
        }
    },
    'KEY': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'auth-token'
    }
}

api = Blueprint('api', __name__, template_folder = '../templates')
apisec = Api( app=api, doc='/redoc', version='0.0.1',title='Logstr Api', \
description='''Get the current weather, daily forecast for 16 days, and a
    three-hour-interval forecast for 5 days for your city. Helpful stats,
    graphics, and this day in history charts are available for your reference.
    Interactive maps show precipitation, clouds, pressure, wind around your
    location stations. Data is available in JSON, XML, or HTML format. **Note**:
    This sample Swagger file covers the `current` endpoint only from the
    OpenWeatherMap API. <br/><br/> **Note**: All parameters are optional, but
    you must select at least one parameter. Calling the API by city ID (using
    the `id` parameter) will provide the most precise location results.''', authorizations=authorizations)

info = apisec.namespace('Information', \
description='**Note:** This operation is only available if you have [Invoice\
        Settlement](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement)\
        enabled. The Invoice Settlement feature is generally available as of Zuora\
        Billing Release 296 (March 2021). This feature includes Unapplied Payments,\
        Credit and Debit Memo, and Invoice Item Settlement. If you want to enable\
        Invoice Settlement, see [Invoice Settlement Enablement and Checklist Guide](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/Invoice_Settlement_Migration_Checklist_and_Guide)\
        for more information. \n\nCreates an ad-hoc credit memo from a product rate\
        plan charge. Zuora supports the creation of credit memos from any type of\
        product rate plan charge. The charges can also have any amount and any charge\
        model, except for discout charge models. \n\nWhen credit memos are created\
        from product rate plan charges, the specified amount with decimal places\
        is now validated based on the decimal places supported by each currency.\n\
        \nYou can create a credit memo only if you have the user permission. See [Billing\
        Roles](https://knowledgecenter.zuora.com/CF_Users_and_Administrators/A_Administrator_Settings/User_Roles/d_Billing_Roles)\
        for more information.\n\nFor a use case of this operation, see [Create credit\
        Settlement](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement)\
        enabled. The Invoice Settlement feature is generally available as of Zuora\
        Billing Release 296 (March 2021). This feature includes Unapplied Payments,\
        Credit and Debit Memo, and Invoice Item Settlement. If you want to enable\
        Invoice Settlement, see [Invoice Settlement Enablement and Checklist Guide](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/Invoice_Settlement_Migration_Checklist_and_Guide)\
        for more information. \n\nCreates an ad-hoc credit memo from a product rate\
        plan charge. Zuora supports the creation of credit memos from any type of\
        product rate plan charge. The charges can also have any amount and any charge\
        model, except for discout charge models. \n\nWhen credit memos are created\
        from product rate plan charges, the specified amount with decimal places\
        is now validated based on the decimal places supported by each currency.\n\
        \nYou can create a credit memo only if you have the user permission. See [Billing\
        Roles](https://knowledgecenter.zuora.com/CF_Users_and_Administrators/A_Administrator_Settings/User_Roles/d_Billing_Roles)\
        for more information.\n\nFor a use case of this operation, see [Create credit\
        memo](https://www.zuora.com/developer/api-guides/#Create-credit-memo).\n', \
path='/')

from . import schema
from .routes import auth, heat, org, appuser, \
    team, project, view, sessionuser, record, session

CORS(api, resources={r"/api/*": {"origins": "*"}})

uploader = apisec.parser()
uploader.add_argument('file', location='files', type=FileStorage, required=True, help="You must parse a file")
uploader.add_argument('name', location='form', type=str, required=True, help="Name cannot be blank")

apisec.add_namespace(auth)
apisec.add_namespace(heat)
apisec.add_namespace(org)
apisec.add_namespace(appuser)
apisec.add_namespace(team)
apisec.add_namespace(project)
apisec.add_namespace(view)
apisec.add_namespace(sessionuser)
apisec.add_namespace(record)
apisec.add_namespace(session)

# The token decorator to protect my routes
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'auth-token' in request.headers:
            token = request.headers['auth-token']
            try:
                data = jwt.decode(token, app.config.get('SECRET_KEY'))
            except:
                return {'message': 'Token is invalid.'}, 403
        if not token:
            return {'message': 'Token is missing or not found.'}, 401
        if data:
            pass
        return f(*args, **kwargs)
    return decorated

@apisec.documentation
@apisec.vendor({
    'logo': {
      'url': 'https://redocly.github.io/redoc/example-logo.png',
      'backgroundColor': '#FFFFFF',
      'altText': 'Example logo'
    }
})
def docs():
    return render_template('redoc.html')


@info.doc(responses={ 201: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error' })
@info.route('/')
class appinfo(Resource):
    @info.doc(description='Get\'s app info')
    @info.marshal_with(schema.appinfo)
    def get(self):
        app = {
            'name':'Logstr api',
            'version': '0.0.1',
            'date': datetime.utcnow(),
            'author': 'Leslie Etubo T., Gaston Nkoh C.',
            'description': 'This is an API to interact with the logstr application'
        }
        return app
        