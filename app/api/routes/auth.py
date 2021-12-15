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
description='This contains data for the **user** and content belonging to the \
application to be shared. The android and iOS application will make calls from \
these endpoints. Tokens will be the method of security with two tokens, a  \
refresh `token` ( **30 days span** ) and a normal token ( **7 days** ) ', \
path='/security')

@auth.doc(responses={ 200: 'OK successful', 201: 'Creation successful', 301: 'Redirect', 400: 'Invalid Argument please check', 401: 'Forbidden Access', 500: 'Mapping Key Error or Internal server error' },
    params= { 'id': 'Specify the Id associated with the person' , 
    'name': 'Specify the name associated with the person' }
    )


@auth.route('/login')
class Login(Resource):
    @auth.doc(description='User enter their `number` and a `code` is sent via **sms** to that number. If an accoutn exist \
        for that number, the code is then authenticated and if successfull the user proceeds to dashboard.')
    #@auth.expect(schema.logindata)
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
        usernumber = postdata['number']
        code = postdata['verification_code'] if postdata.get('verification_code') is not None else None
        authtoken = jwt.encode(
            {
                'user': 'logstr',
                'number': 'logstr',
                'exp': datetime.utcnow() + timedelta(days=30),
                'iat': datetime.utcnow()
            },
            app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
        string_token = str(authtoken)
        return {
            'result': 'Welcome logstr',
            'token': string_token,
            'status': 1
        }, 201

@auth.route('/signup')
class Signup(Resource):
    @auth.doc(description='User enters their `username` and `number`.\
         These credentials are sent to server and an **sms** is sent to the users phone. \
             Only after the code sent in the sms is authenticated will the user account be created.')
    #@auth.expect(schema.signupdata)
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
        business = postdata['bus_type'] or None
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
        