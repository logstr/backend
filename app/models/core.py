from app import db
from time import time
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app as app
import redis, rq, jwt, uuid, enum, config, pytz
from app.billing import Card as PaymentCard, Subscription as PaymentSubscription, \
    Coupon as PaymentCoupon, Invoice as PaymentInvoice

import datetime
from collections import OrderedDict
from os import urandom
from binascii import hexlify

import pytz
from sqlalchemy import or_, and_

from sqlalchemy.ext.hybrid import hybrid_property
from app.billing import dollars_to_cents, cents_to_dollars
    


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
    profile_pic = db.Column(db.String(80))
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

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return Users.query.get(id)

    def send_reset(self, name, *args, **kwargs):
        passivesend = app.high_queue.enqueue('app.jobs.job.' + name, *args, **kwargs)
        task = Task(id=passivesend.get_id(), name='sendreset', description='Sends a reset password email', session_id=self)
        db.session.add(task)
        return task
        
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
    x = db.Column(db.Integer)
    y = db.Column(db.Integer)
    value = db.Column(db.Integer)
    event_type = db.Column(db.Enum(logevents))
    event = db.Column(db.JSON)
    timeOffset = db.Column(db.BigInteger)
    event_info = db.Column(db.JSON)
    sessions_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))

    def __init__(self, xdata, ydata, value, event_type_key, event, \
        session_id, timeOffset, event_info):
        self.x = xdata
        self.y = ydata
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

class Subscriptions(db.Model):
    __tablename__ = "subscriptions"
    id = db.Column(db.Integer, primary_key=True)

    # Relationships.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', \
    onupdate='CASCADE', ondelete='CASCADE'), \
        index=True, nullable=False)
    # Subscription details.
    plan = db.Column(db.String(128))
    coupon = db.Column(db.String(32))

    def __init__(self, user_id, plan, coupon):
        self.user_id = user_id
        self.plan = plan
        self.coupon = coupon

    @classmethod
    def get_plan_by_id(cls, plan):
        """
        Pick the plan based on the plan identifier.
        :param plan: Plan identifier
        :type plan: str
        :return: dict or None
        """
        for key, value in config.STRIPE_PLANS.iteritems():
            if value.get('id') == plan:
                return config.STRIPE_PLANS[key]

        return None

    @classmethod
    def get_new_plan(self, keys):
        """
        Pick the plan based on the plan identifier.
        :param keys: Keys to look through
        :type keys: list
        :return: str or None
        """
        for key in keys:
            split_key = key.split('submit_')

            if isinstance(split_key, list) and len(split_key) == 2:
                if self.get_plan_by_id(split_key[1]):
                    return split_key[1]

        return None

    def create(self, user=None, name=None, plan=None, coupon=None, token=None):
        """
        Create a recurring subscription.
        :param user: User to apply the subscription to
        :type user: User instance
        :param name: User's billing name
        :type name: str
        :param plan: Plan identifier
        :type plan: str
        :param coupon: Coupon code to apply
        :type coupon: str
        :param token: Token returned by javascript
        :type token: str
        :return: bool
        """
        if token is None:
            return False

        if coupon:
            self.coupon = coupon.upper()

        customer = PaymentSubscription.create(token=token,
                                              email=user.email,
                                              plan=plan,
                                              coupon=self.coupon)

        # Update the user account.
        user.payment_id = customer.id
        user.name = name
        user.cancelled_subscription_on = None

        # Set the subscription details.
        self.user_id = user.id
        self.plan = plan

        # Redeem the coupon.
        if coupon:
            coupon = Coupon.query.filter(Coupon.code == self.coupon).first()
            coupon.redeem()

        # Create the credit card.
        credit_card = CreditCard(user_id=user.id,
                                 **CreditCard.extract_card_params(customer))

        db.session.add(user)
        db.session.add(credit_card)
        db.session.add(self)

        db.session.commit()

        return True

    def update(self, user=None, coupon=None, plan=None):
        """
        Update an existing subscription.
        :param user: User to apply the subscription to
        :type user: User instance
        :param coupon: Coupon code to apply
        :type coupon: str
        :param plan: Plan identifier
        :type plan: str
        :return: bool
        """
        PaymentSubscription.update(user.payment_id, coupon, plan)

        user.subscription.plan = plan
        if coupon:
            user.subscription.coupon = coupon
            coupon = Coupon.query.filter(Coupon.code == coupon).first()

            if coupon:
                coupon.redeem()

        db.session.add(user.subscription)
        db.session.commit()

        return True

    def cancel(self, user=None, discard_credit_card=True):
        """
        Cancel an existing subscription.
        :param user: User to apply the subscription to
        :type user: User instance
        :param discard_credit_card: Delete the user's credit card
        :type discard_credit_card: bool
        :return: bool
        """
        PaymentSubscription.cancel(user.payment_id)

        user.payment_id = None
        user.cancelled_subscription_on = datetime.datetime.now(pytz.utc)

        db.session.add(user)
        db.session.delete(user.subscription)

        # Explicitly delete the credit card because the FK is on the
        # user, not subscription so we can't depend on cascading deletes.
        # This is for cases where you may want to keep a user's card
        # on file even if they cancelled.
        if discard_credit_card:
            db.session.delete(user.credit_card)

        db.session.commit()

        return True

    def update_payment_method(self, user=None, name=None, token=None):
        """
        Update the subscription.
        :param user: User to apply the subscription to
        :type user: User instance
        :param name: User's billing name
        :type name: str
        :param token: Token returned by javascript
        :type token: str
        :return: bool
        """
        if token is None:
            return False

        customer = PaymentCard.update(user.payment_id, token)
        user.name = name

        # Create the new credit card.
        credit_card = CreditCard(user_id=user.id,
                                 **CreditCard.extract_card_params(customer))

        db.session.add(user)
        db.session.delete(user.credit_card)
        db.session.add(credit_card)

        db.session.commit()

        return True

class Coupon(db.Model):
    DURATION = OrderedDict([
        ('forever', 'Forever'),
        ('once', 'Once'),
        ('repeating', 'Repeating')
    ])

    __tablename__ = 'coupons'
    id = db.Column(db.Integer, primary_key=True)

    # Coupon details.
    code = db.Column(db.String(32), index=True, unique=True)
    duration = db.Column(db.Enum(*DURATION, name='duration_types'),
                         index=True, nullable=False, server_default='forever')
    amount_off = db.Column(db.Integer())
    percent_off = db.Column(db.Integer())
    currency = db.Column(db.String(8))
    duration_in_months = db.Column(db.Integer())
    max_redemptions = db.Column(db.Integer(), index=True)
    redeem_by = db.Column(db.DateTime(), index=True)
    times_redeemed = db.Column(db.Integer(), index=True,
                               nullable=False, default=0)
    valid = db.Column(db.Boolean(), nullable=False, server_default='1')

    def __init__(self, **kwargs):
        if self.code:
            self.code = self.code.upper()
        else:
            self.code = Coupon.random_coupon_code()

        # Call Flask-SQLAlchemy's constructor.
        super(Coupon, self).__init__(**kwargs)

    @hybrid_property
    def redeemable(self):
        """
        Return coupons that are still redeemable. Coupons will become invalid
        once they run out on save. We want to explicitly do a date check to
        avoid having to hit Stripe's API to get back potentially valid codes.
        :return: SQLAlchemy query object
        """
        is_redeemable = or_(self.redeem_by.is_(None),
                            self.redeem_by >= datetime.datetime.now(pytz.utc))

        return and_(self.valid, is_redeemable)

    @classmethod
    def search(self, query):
        """
        Search a resource by 1 or more fields.
        :param query: Search query
        :type query: str
        :return: SQLAlchemy filter
        """
        if not query:
            return ''

        search_query = '%{0}%'.format(query)

        return or_(Coupon.code.ilike(search_query))

    @classmethod
    def random_coupon_code(self):
        """
        Create a human readable random coupon code.
        Inspired by:
          http://stackoverflow.com/a/22333563
        :return: str
        """
        random_string = hexlify(urandom(20))
        long_code = random_string.translate(str.maketrans('0123456789abcdefghij',
                                                      '234679QWERTYUPADFGHX'))

        short_code = '{0}-{1}-{2}'.format(long_code[0:4],
                                          long_code[5:9],
                                          long_code[10:14])

        return short_code

    @classmethod
    def expire_old_coupons(self, compare_datetime=None):
        """
        Invalidate coupons that are past their redeem date.
        :param compare_datetime: Time to compare at
        :type compare_datetime: date
        :return: The result of updating the records
        """
        if compare_datetime is None:
            compare_datetime = datetime.datetime.now(pytz.utc)

        condition = Coupon.redeem_by <= compare_datetime
        Coupon.query.filter(condition) \
            .update({Coupon.valid: not Coupon.valid})

        return db.session.commit()

    @classmethod
    def create(self, params):
        """
        Return whether or not the coupon was created successfully.
        :return: bool
        """
        payment_params = params

        payment_params['code'] = payment_params['code'].upper()

        if payment_params.get('amount_off'):
            payment_params['amount_off'] = \
                dollars_to_cents(payment_params['amount_off'])

        PaymentCoupon.create(**payment_params)

        if 'id' in payment_params:
            payment_params['code'] = payment_params['id']
            del payment_params['id']

        if 'redeem_by' in payment_params:
            if payment_params.get('redeem_by') is not None:
                params['redeem_by'] = payment_params.get('redeem_by').replace(
                    tzinfo=pytz.UTC)

        coupon = Coupon(**payment_params)

        db.session.add(coupon)
        db.session.commit()

        return True

    @classmethod
    def bulk_delete(self, ids):
        """
        Override the general bulk_delete method because we need to delete them
        one at a time while also deleting them on Stripe.
        :param ids: List of ids to be deleted
        :type ids: list
        :return: int
        """
        delete_count = 0

        for id in ids:
            coupon = Coupon.query.get(id)

            if coupon is None:
                continue

            # Delete on Stripe.
            stripe_response = PaymentCoupon.delete(coupon.code)

            # If successful, delete it locally.
            if stripe_response.get('deleted'):
                coupon.delete()
                delete_count += 1

        return delete_count

    @classmethod
    def find_by_code(self, code):
        """
        Find a coupon by its code.
        :param code: Coupon code to find
        :type code: str
        :return: Coupon instance
        """
        formatted_code = code.upper()
        coupon = Coupon.query.filter(Coupon.redeemable,
                                     Coupon.code == formatted_code).first()

        return coupon

    def redeem(self):
        """
        Update the redeem stats for this coupon.
        :return: Result of saving the record
        """
        self.times_redeemed += 1

        if self.max_redemptions:
            if self.times_redeemed >= self.max_redemptions:
                self.valid = False

        return db.session.commit()

    def serialize(self):
        """
        Return JSON fields to render the coupon code status.
        :return: dict
        """
        params = {
            'duration': self.duration,
            'duration_in_months': self.duration_in_months,
        }

        if self.amount_off:
            params['amount_off'] = cents_to_dollars(self.amount_off)

        if self.percent_off:
            params['percent_off'] = self.percent_off,

        return params

class CreditCard(db.Model):
    IS_EXPIRING_THRESHOLD_MONTHS = 2

    __tablename__ = 'credit_cards'
    id = db.Column(db.Integer, primary_key=True)

    # Relationships.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id',
                                                  onupdate='CASCADE',
                                                  ondelete='CASCADE'),
                        index=True, nullable=False)

    # Card details.
    brand = db.Column(db.String(32))
    last4 = db.Column(db.Integer)
    exp_date = db.Column(db.Date, index=True)
    is_expiring = db.Column(db.Boolean(), nullable=False, server_default='0')

    def __init__(self, **kwargs):
        # Call Flask-SQLAlchemy's constructor.
        super(CreditCard, self).__init__(**kwargs)
    
    def timedelta_months(months, compare_date=None):
        """
        Return a new datetime with a month offset applied.
        :param months: Amount of months to offset
        :type months: int
        :param compare_date: Date to compare at
        :type compare_date: date
        :return: datetime
        """
        if compare_date is None:
            compare_date = datetime.date.today()

        delta = months * 365 / 12
        compare_date_with_delta = compare_date + datetime.timedelta(delta)

        return compare_date_with_delta

    @classmethod
    def is_expiring_soon(self, compare_date=None, exp_date=None):
        """
        Determine whether or not this credit card is expiring soon.
        :param compare_date: Date to compare at
        :type compare_date: date
        :param exp_date: Expiration date
        :type exp_date: date
        :return: bool
        """
        return exp_date <= self.timedelta_months(
            CreditCard.IS_EXPIRING_THRESHOLD_MONTHS, compare_date=compare_date)

    @classmethod
    def mark_old_credit_cards(self, compare_date=None):
        """
        Mark credit cards that are going to expire soon or have expired.
        :param compare_date: Date to compare at
        :type compare_date: date
        :return: Result of updating the records
        """
        today_with_delta = self.timedelta_months(
            CreditCard.IS_EXPIRING_THRESHOLD_MONTHS, compare_date)

        CreditCard.query.filter(CreditCard.exp_date <= today_with_delta) \
            .update({CreditCard.is_expiring: True})

        return db.session.commit()

    @classmethod
    def extract_card_params(self, customer):
        """
        Extract the credit card info from a payment customer object.
        :param customer: Payment customer
        :type customer: Payment customer
        :return: dict
        """
        card_data = customer.cards.data[0]
        exp_date = datetime.date(card_data.exp_year, card_data.exp_month, 1)

        card = {
            'brand': card_data.brand,
            'last4': card_data.last4,
            'exp_date': exp_date,
            'is_expiring': CreditCard.is_expiring_soon(exp_date=exp_date)
        }

        return

class Invoice(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)

    # Relationships.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id',
                                                  onupdate='CASCADE',
                                                  ondelete='CASCADE'),
                        index=True, nullable=False)

    # Invoice details.
    plan = db.Column(db.String(128), index=True)
    receipt_number = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    period_start_on = db.Column(db.Date)
    period_end_on = db.Column(db.Date)
    currency = db.Column(db.String(8))
    tax = db.Column(db.Integer())
    tax_percent = db.Column(db.Float())
    total = db.Column(db.Integer())

    # De-normalize the card details so we can render a user's history properly
    # even if they have no active subscription or changed cards at some point.
    brand = db.Column(db.String(32))
    last4 = db.Column(db.Integer)
    exp_date = db.Column(db.Date, index=True)

    def __init__(self, **kwargs):
        # Call Flask-SQLAlchemy's constructor.
        super(Invoice, self).__init__(**kwargs)

    @classmethod
    def parse_from_event(self, payload):
        """
        Parse and return the invoice information that will get saved locally.
        :return: dict
        """
        data = payload['data']['object']
        plan_info = data['lines']['data'][0]['plan']

        period_start_on = datetime.datetime.utcfromtimestamp(
            data['lines']['data'][0]['period']['start']).date()
        period_end_on = datetime.datetime.utcfromtimestamp(
            data['lines']['data'][0]['period']['end']).date()

        invoice = {
            'payment_id': data['customer'],
            'plan': plan_info['name'],
            'receipt_number': data['receipt_number'],
            'description': plan_info['statement_descriptor'],
            'period_start_on': period_start_on,
            'period_end_on': period_end_on,
            'currency': data['currency'],
            'tax': data['tax'],
            'tax_percent': data['tax_percent'],
            'total': data['total']
        }

        return invoice

    @classmethod
    def parse_from_api(self, payload):
        """
        Parse and return the invoice information we are interested in.
        :return: dict
        """
        plan_info = payload['lines']['data'][0]['plan']
        date = datetime.datetime.utcfromtimestamp(payload['date'])

        invoice = {
            'plan': plan_info['name'],
            'description': plan_info['statement_descriptor'],
            'next_bill_on': date,
            'amount_due': payload['amount_due'],
            'interval': plan_info['interval']
        }

        return invoice

    @classmethod
    def prepare_and_save(self, parsed_event):
        """
        Potentially save the invoice after argument the event fields.
        :param parsed_event: Event params to be saved
        :type parsed_event: dict
        :return: Stripe invoice object or None
        """
        # Avoid circular imports.

        # Only save the invoice if the user is valid at this point.
        id = parsed_event.get('payment_id')
        user = Users.query.filter((Users.payment_id == id)).first()

        if user and user.credit_card:
            parsed_event['user_id'] = user.id
            parsed_event['brand'] = user.credit_card.brand
            parsed_event['last4'] = user.credit_card.last4
            parsed_event['exp_date'] = user.credit_card.exp_date

            del parsed_event['payment_id']

            invoice = Invoice(**parsed_event)
            return invoice.save()

        return None

    @classmethod
    def upcoming(self, customer_id):
        """
        Return the upcoming invoice item.
        :param customer_id: Stripe customer id
        :type customer_id: int
        :return: Stripe invoice object
        """
        invoice = PaymentInvoice.upcoming(customer_id)

        return Invoice.parse_from_api(invoice)