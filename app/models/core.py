from app import db
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import enum

class logevents(enum.Enum):
    click = 'click'
    scroll = 'scroll'
    move = 'move'


class Users (db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True)
    uuid = db.Column(db.Unicode, unique=True)
    emailaddress = db.Column(db.String(60))
    phone = db.Column(db.String(30))
    password = db.Column(db.String(30))
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
    id = db.Column(db.Integer, primary_key = True)
    uuid = db.Column(db.String(60), unique=True)
    name = db.Column(db.String(30))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, name, update_at, user_id):
        self.uuid = uuid.uuid4().hex
        self.name = name
        self.updated_at = update_at
        self.user_id = user_id
        self.created_at = datetime.utcnow()
        

    def __repr__(self):
        return '<User %r>' % self.name

class Teams (db.Model):
    __tablename__ = "teams"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(30))
    uuid = db.Column(db.String(60), unique=True)
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
        return '<User %r>' % self.name

class Sessions (db.Model):
    __tablename__ = "sessions"
    id = db.Column(db.Integer, primary_key = True)
    uuid = db.Column(db.String(60), primary_key = True, unique=True)
    ip_address = db.Column(db.String(60))
    device = db.Column(db.String(60))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    navigator_info = db.Column(db.JSON)
    projects_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    projects = db.relationship('Projects', foreign_keys=projects_id)
    created_at = db.Column(db.DateTime)

    def __init__(self, ip, device, startTime, endTime, project, project_id, navigator):
        self.uuid = uuid.uuid4().hex
        self.ip_address = ip
        self.device = device
        self.start_time = startTime
        self.end_time = endTime
        self.navigator_info = navigator
        self.projects = project
        self.projects_id = project_id
        self.created_at = datetime.utcnow()
        

    def __repr__(self):
        return '<User %r>' % self.uuid

class Projects (db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key = True)
    uuid = db.Column(db.String(60), unique=True)
    name = db.Column(db.String(60))
    platform = db.Column(db.String(60))
    teams_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    organizations_id = db.Column('organizations_id', db.Integer, db.ForeignKey('organizations.id'))

    teams = db.relationship('Teams', foreign_keys=teams_id)
    organizations = db.relationship('Organizations', foreign_keys=organizations_id)

    def __init__(self, name, platform, team_id, organization_id):
        self.uuid = uuid.uuid4().hex
        self.name = name
        self.platform = platform
        self.team_id = team_id
        self.organization_id = organization_id
        self.created_at = datetime.utcnow()
        

    def __repr__(self):
        return '<User %r>' % self.name

class Heatmaps (db.Model):
    __tablename__ = "heatmaps"
    id = db.Column(db.Integer, primary_key = True)
    xdata = db.Column(db.Integer)
    ydata = db.Column(db.Integer)
    value = db.Column(db.Integer)
    event_type = db.Column(db.Enum(logevents))
    event = db.Column(db.JSON)
    sessions_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))
    sessions_uuid = db.Column(db.String(60), db.ForeignKey('sessions.uuid'))
    timestamp = db.Column(db.DateTime)
    event_info = db.Column(db.JSON)

    def __init__(self, xdata, ydata, value, event_type_key, event, \
        session_id, session_uuid, timestamp, event_info):
        self.uuid = uuid.uuid4().hex
        self.xdata = xdata
        self.ydata = ydata
        self.value = value
        self.event_type = event_type_key
        self.event = event
        self.sessions_id = session_id
        self.sessions_uuid = session_uuid
        self.timestamp = timestamp
        self.event_info = event_info
        

    def __repr__(self):
        return '<User %r>' % self.uuid

