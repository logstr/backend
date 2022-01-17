from flask_restx import Namespace, Resource, fields
from app.api import schema
from app import db, oauth
from app.models import Users
from datetime import datetime
from datetime import  timedelta
import jwt, uuid, os
from flask import current_app as app, url_for, redirect
from flask import Blueprint, render_template, abort, request


auth = Namespace('Authentication', \
description='This route authenticates a user and creates a token for user to keep logging into the system.\
Tokens will contain some more data about the user that can be used to later on identify the user after authentication is completed  \
refresh `token` ( **30 days span** ) and a normal token ( **7 days** ) ', \
path='/security')

@auth.doc(responses={ 200: 'OK successful', \
    201: 'Creation successful', 301: 'Redirect', 400: 'Invalid Argument please check', \
    401: 'Forbidden Access', 500: 'Mapping Key Error or Internal server error' })
@auth.route('/login')
class Login(Resource):
    @auth.doc(description='User enter their `firstname` or `email` and a `password`. If an account exist \
        for that user, the user is then authenticated and if successfull the user `token` is generated')
    @auth.expect(schema.logindata)
    def post(self):
        postdata = request.get_json()
        if postdata:
            firstname= postdata['firstname']
            password = postdata['password']

            user = Users.query.filter((Users.first_name == firstname.lower()) | (Users.emailaddress == firstname.lower())).first()
            if user:
                if user.verify_password(password):
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
                else:
                    return {
                        'result': 'Please check password or username',
                        'status': False
                    }, 200
            else:
                return {
                    'result': 'Please check password or username',
                    'status': False
                }, 200
        else:
            return {
                'result': 'Invalid data',
                'status': False
            }, 200

@auth.route('/signup')
class Signup(Resource):
    @auth.doc(description='User enters their `username` and `password`.\
         These credentials are sent to server and a **token** is returned to the users after the account has been created.')
    @auth.expect(schema.signupdata)
    def post(self):
        postdata = request.get_json()
        if postdata:
            firstname = postdata['firstname']
            lastname = postdata['lastname']
            email = postdata['email']
            number = postdata['number']
            password = postdata['password']
            team = postdata['team'] if 'team' in postdata else None
            organization = postdata['organization'] if 'organization' in postdata else None

            existing_user = Users.query.filter_by(first_name=firstname).first()
            if existing_user:
                return {
                    'result': 'Account already exist, please login',
                    'status': False
                }, 200
            else:
                user = Users(email, number, password, firstname, lastname, \
                     profile_pic=None, update_at=None, teams_id=team, organizations_id=organization)
                db.session.add(user)
                db.session.commit()
            return {
                'response': 'Account created successfully. Please proceed to login',
                'status': True
            }, 201
        else:
            return {
                'response': 'Invalid Data',
                'status': False
            }, 200