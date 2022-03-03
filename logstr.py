'''
App entry point
'''
from datetime import time, timedelta, datetime
from sys import version
from time import sleep
from flask import redirect, url_for, request, session, jsonify
from flask.templating import render_template
import jwt
from app import create_app, graphql, sio, oauth, db
from flask_graphql import GraphQLView
from app.graphql.schema import schema
from app.graphql.template import TEMPLATE, GRAPHIQL_VERSION
from app.jobs.job import send_email
from app.models.core import Users

app = create_app('dev')

logstr = '{}\n\033[92m{}\033[00m\n\033[92m{}\033[00m'

google = oauth.remote_app(
    'google',
    consumer_key=app.config.get('GOOGLE_CLIENT_ID'),
    consumer_secret=app.config.get('GOOGLE_CLIENT_SECRET'),
    request_token_params={
        'scope': ['email','profile']
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

@app.route('/')
def docs():
    return redirect(url_for('api.doc'))

@app.route('/email')
def email():
    send_email('Weekly Web Reports for Logstr app',
                sender=app.config['ADMINS'][0], recipients=['touchone0001@gmail.com'],
                text_body=render_template('report.txt'),
                html_body=render_template('report.html'),
                attachments=None,
                sync=True)
    return 'done'

@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/login/authorized')
def authorized():
    resp = google.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (resp['access_token'], '')
    me = google.get('userinfo')
    data = me.data
    if me:
        firstname = data['given_name']
        lastname = data['family_name']
        email = data['email']
        number = None
        password = data['id']
        team = None
        organization = None

        existing_user = Users.query.filter_by(emailaddress=email).first()
        if existing_user:
            authtoken = jwt.encode(
                {
                    'user': existing_user.first_name,
                    'uuid': existing_user.uuid,
                    'exp': datetime.utcnow() + timedelta(days=7),
                    'iat': datetime.utcnow()
                },
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
            string_token = str(authtoken)
            return {
                'result': 'Welcome ' + firstname,
                'token': string_token,
                'status': True
            }, 201
        else:
            user = Users(email, number, password, firstname, lastname, \
                    profile_pic=data['picture'], update_at=None, teams_id=team, organizations_id=organization)
            db.session.add(user)
            db.session.commit()
            authtoken = jwt.encode(
                {
                    'user': user.first_name,
                    'uuid': user.uuid,
                    'exp': datetime.utcnow() + timedelta(days=7),
                    'iat': datetime.utcnow()
                },
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
            string_token = str(authtoken)
            return {
                'result': 'Welcome ' + user.first_name,
                'token': string_token,
                'status': True
            }, 201

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

app.add_url_rule('/api/graphql', view_func=GraphQLView.as_view(
    'graphql',
    schema=schema,
    graphiql=True,
    graphiql_version = GRAPHIQL_VERSION,
    graphiql_html_title = 'Logstr-Graphql',
    graphiql_template = TEMPLATE
))

if __name__ == "__main__":
    print(logstr.format('LOGSTR API','[+] Ran system checks','[+] Starting api ...'))
    sio.run(
        app = app,
        host=app.config.get('HOST'),
        port=app.config.get('PORT'),
        debug=app.config.get('DEBUG')
    )