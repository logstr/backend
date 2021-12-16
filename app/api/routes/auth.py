from flask_restplus import Namespace, Resource, fields
from app.api import schema
from app import db
from app.models import Users
from datetime import datetime
from datetime import  timedelta
import jwt, uuid, os
from flask import current_app as app
from flask import Blueprint, render_template, abort, request

auth = Namespace('Authentication', \
description='This route authenticates a user and creates a token for user to keep logging into the system.\
Tokens will contain some more data about the user that can be used to later on identify the user after authentication is completed  \
refresh `token` ( **30 days span** ) and a normal token ( **7 days** ) ', \
path='/security')

@auth.doc(responses={ 200: 'OK successful', 201: 'Creation successful', 301: 'Redirect', 400: 'Invalid Argument please check', 401: 'Forbidden Access', 500: 'Mapping Key Error or Internal server error' },
    params= { 
        'firstname': 'Firstname of the user' , 
        'password': 'password of the user' }
    )


@auth.route('/login')
class Login(Resource):
    @auth.doc(description='User enter their `firstname` or `email` and a `password`. If an account exist \
        for that user, the user is then authenticated and if successfull the user `token` is generated')
    @auth.expect(schema.logindata)
    @auth.vendor(
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
    def post(self):
        postdata = request.get_json()
        if postdata:
            firstname= postdata['first_name']
            password = postdata['password']

            user = Users.query.filter((Users.first_name == firstname.lower()) | (Users.email == firstname.lower())).first()
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
    @auth.vendor(
        {
            'x-codeSamples':
            [
                { 
                    "lang": "JavaScript",
                    "source": "console.log('Hello World');" 
                },
                { 
                    "lang": "Curl",
                    "source": "curl -X POST 'http://127.0.0.1:5000/api/security/signup' -H  'accept: application/json' -H  'Content-Type: application/json' -d '{  \"username\": \"Boogie\",  \"number\": \"+237650221486\",  \"bus_type\": \"Personal\",  \"verification_code\": \"\"}' "
                }
            ]
        })
    def post(self):
        postdata = request.get_json()
        username = postdata['username']
        usernumber = postdata['number']
        existing_user = Users.query.filter_by(usernumber=usernumber).first()
        if existing_user is not None:
            return {
                'result': 'Account already exist, please login',
                'status': 0
            }, 301
        else:
            user = Users(username, usernumber=usernumber, email=None, ip_addr=None, \
                verified=False, bio=None, profile_pic=None)
            db.session.add(user)
            db.session.commit()
        return {
            'response': 'Account created successfully. Please proceed to login',
            'status': 1
        }, 201   
        