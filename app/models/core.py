from app import db
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import uuid, enum
from flask import current_app as app
import redis
import rq



class logevents(enum.Enum):
    click = 'click'
    scroll = 'scroll'
    move = 'move'

class Users (db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    uuid = db.Column(db.Unicode, unique=True)
    emailaddress = db.Column(db.String(60))
    phone = db.Column(db.String(30))
    password = db.Column(db.String(256))
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    ptofile_pic = db.Column(db.String(80))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    teams = db.relationship('Teams', backref='owner', lazy='dynamic')
    organizations = db.relationship('Organizations', backref='owner', lazy='dynamic')

    def __init__(self, emailadress, phone, password, \
         first_name, last_name, profile_pic, update_at, \
             teams_id, organizations_id ):
        self.uuid = uuid.uuid4().hex
        self.emailaddress = emailadress
        self.phone = phone
        self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name
        self.profile_pic = profile_pic
        self.updated_at = update_at
        self.teams_id = teams_id
        self.organizations_id = organizations_id
        self.created_at = datetime.utcnow()
        
    def verify_password(self, password):
        return check_password_hash(self.password, password)
        
    def __repr__(self):
        return '<User %r>' % self.emailaddress

class Organizations (db.Model):
    __tablename__ = "organizations"
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    uuid = db.Column(db.String(60), unique=True)
    name = db.Column(db.String(30))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    projects = db.relationship('Projects', backref='orgprojects', lazy='dynamic')

    def __init__(self, name, update_at, user_id):
        self.uuid = uuid.uuid4().hex
        self.name = name
        self.updated_at = update_at
        self.user_id = user_id
        self.created_at = datetime.utcnow()
        

    def __repr__(self):
        return '<Organization %r>' % self.name

class Teams (db.Model):
    __tablename__ = "teams"
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(30))
    uuid = db.Column(db.String(60), primary_key = True, unique=True)
    size = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    organizations_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    organizations = db.relationship('Organizations', foreign_keys=organizations_id)

    def __init__(self, name, size, update_at, user_id, organization_id):
        self.uuid = uuid.uuid4().hex
        self.name = name
        self.size = size
        self.updated_at = update_at
        self.user_id = user_id
        self.organizations_id = organization_id
        self.created_at = datetime.utcnow()
        

    def __repr__(self):
        return '<Team %r>' % self.name

class Sessions (db.Model):
    __tablename__ = "sessions"
    id = db.Column(db.Integer, primary_key = True, unique=True, autoincrement=True)
    uuid = db.Column(db.String(60), primary_key = True, unique=True)
    ip_address = db.Column(db.String(60))
    device = db.Column(db.String(60))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    navigator_info = db.Column(db.JSON)
    created_at = db.Column(db.DateTime)
    projects_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    sessions_user_id = db.Column(db.Integer, db.ForeignKey('sessionuser.id'))

    def __init__(self, ip, device, startTime, endTime, project_id, navigator, sessionuser):
        self.uuid = uuid.uuid4().hex
        self.ip_address = ip
        self.device = device
        self.start_time = startTime
        self.sessions_user_id = sessionuser
        self.end_time = endTime
        self.navigator_info = navigator
        self.projects_id = project_id
        self.created_at = datetime.utcnow()
        

    def __repr__(self):
        return '<Session %r>' % self.uuid

    def launch_insert(self, name, data, session, *args, **kwargs):
        passiveinsert = app.high_queue.enqueue('app.jobs.job.' + name, data, session, *args, **kwargs)
        task = Task(id=passiveinsert.get_id(), name='addrecord', description='Slow insert task', session_id=self)
        db.session.add(task)
        return task

class Projects (db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key = True)
    uuid = db.Column(db.String(60), unique=True)
    name = db.Column(db.String(60))
    platform = db.Column(db.String(60))
    admin = db.Column('admin', db.Integer, db.ForeignKey('users.id'))
    organizations_id = db.Column('organizations_id', db.Integer, db.ForeignKey('organizations.id'))

    sessions = db.relationship('Sessions', backref='project_sessions', lazy='dynamic')
    usersessions = db.relationship('Sessionuser', backref='sessions', lazy='dynamic')

    def __init__(self, name, appplatform, admin, organization_id):
        self.uuid = uuid.uuid4().hex
        self.name = name
        self.admin = admin
        self.platform = appplatform
        self.organizations_id = organization_id
        self.created_at = datetime.utcnow()
        

    def __repr__(self):
        return '<Project %r>' % self.name

class Heatmaps (db.Model):
    __tablename__ = "heatmaps"
    id = db.Column(db.Integer, primary_key = True, unique=True, autoincrement=True)
    xdata = db.Column(db.Integer)
    ydata = db.Column(db.Integer)
    value = db.Column(db.Integer)
    event_type = db.Column(db.Enum(logevents))
    event = db.Column(db.JSON)
    timeOffset = db.Column(db.BigInteger)
    event_info = db.Column(db.JSON)
    sessions_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))

    def __init__(self, xdata, ydata, value, event_type_key, event, \
        session_id, timeOffset, event_info):
        self.xdata = xdata
        self.ydata = ydata
        self.value = value
        self.event_type = event_type_key
        self.event = event
        self.sessions_id = session_id
        self.timeOffset = timeOffset
        self.event_info = event_info
        

    def __repr__(self):
        return '<Heatmap %r>' % self.id

class Recordings (db.Model):
    __tablename__ = "recordings"
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    type = db.Column(db.Integer)
    data = db.Column(db.JSON)
    timestamp = db.Column(db.BigInteger)
    sessions_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))

    def __init__(self, type, data, timestamp, session_id):
        self.uuid = uuid.uuid4().hex
        self.type = type
        self.data = data
        self.timestamp = timestamp
        self.sessions_id = session_id

    def __repr__(self):
        return '<Heatmap %r>' % self.id

class Views (db.Model):
    __tablename__ = "views"
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    uuid = db.Column(db.String(60), primary_key = True, unique=True)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    title = db.Column(db.String(60))
    slug = db.Column(db.String(500))
    sessions_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))
    sessions_uuid = db.Column(db.String(60), db.ForeignKey('sessions.uuid'))
    created_at = db.Column(db.DateTime)

    def __init__(self, ip, device, startTime, endTime, title, slug):
        self.uuid = uuid.uuid4().hex
        self.start_time = startTime
        self.end_time = endTime
        self.title = title
        self.slug = slug
        self.created_at = datetime.utcnow()
        

    def __repr__(self):
        return '<View %r>' % self.uuid

class Sessionuser (db.Model):
    __tablename__ = "sessionuser"
    id = db.Column(db.Integer, primary_key = True, unique=True, autoincrement=True)
    uuid = db.Column(db.String(60), unique=True)
    name = db.Column(db.String(60))
    email = db.Column(db.String(60))
    created_at = db.Column(db.DateTime)
    projects_id = db.Column(db.Integer, db.ForeignKey('projects.id'))

    usersessions = db.relationship('Sessions', backref='sessions', lazy='dynamic')

    def __init__(self, name, email, project):
        self.uuid = uuid.uuid4().hex
        self.name = name
        self.email = email
        self.projects_id = project
        self.created_at = datetime.utcnow()
        

    def __repr__(self):
        return '<Sessionuser %r>' % self.uuid


class Task(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))
    complete = db.Column(db.Boolean, default=False)

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100
