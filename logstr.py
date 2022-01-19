'''
App entry point
'''
from datetime import time, timedelta
from sys import version
from time import sleep
from flask import redirect, url_for, request, session, jsonify
from flask.templating import render_template
from app import create_app, graphql, sio, oauth
from flask_graphql import GraphQLView
from app.graphql.schema import schema
from app.graphql.template import TEMPLATE, GRAPHIQL_VERSION
from app.jobs.job import send_email

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
                sender=app.config['ADMINS'][0], recipients=['das.sanctity.ds@gmail.com'],
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
    google_token = (resp['access_token'], '')
    me = google.get('userinfo')
    return jsonify({
        "data": me.data,
        "google_token": google_token
        })

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
    print(logstr.format('📦  LOGSTR API','🚒 Ran system checks','[+] Starting api ...'))
    sio.run(
        app = app,
        host=app.config.get('HOST'),
        port=app.config.get('PORT'),
        debug=app.config.get('DEBUG')
    )