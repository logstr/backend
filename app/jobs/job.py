from app.models import Recordings, Heatmaps
from flask import current_app as app
from flask_mail import Message
from app import db, create_app, mail
import json
from threading import Thread



app = create_app('dev')
app.app_context().push()

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def addrecord(postdata, session):
    db.session.bulk_save_objects(
        [
            Recordings(type=i['type'], \
                data=i['data'], \
                    timestamp=i['timestamp'], \
                        session_id=session)
            for i in json.loads(postdata['recdata'])['recordings']
        ]
    )
    db.session.commit()
    return session


def addheat(postdata, session):
    for i in json.loads(postdata['recdata'])['recordings']:
        if i['type'] == 3:
            heat = i['data']
            if 'source' in heat:
                if heat['source'] == 1:
                    if 'positions' in heat:
                        for j in heat['positions']:
                            for z in j:
                                x = j['x']
                                y = j['y']
                                timeOffset = j['timeOffset']
                                data = Heatmaps(x, y, value=None, event_type_key='move', event=heat['positions'], session_id=session, timeOffset=timeOffset, event_info=heat['positions'])
                                db.session.add(data)
                if heat['source'] == 2 and 'x' in heat:
                    x = heat['x']
                    y = heat['y']
                    value = heat['id']
                    data = Heatmaps(x, y, value, 'click', event=heat['source'], session_id=session, timeOffset=None, event_info=heat['source'])
                    db.session.add(data)
                if heat['source'] == 3:
                    x = heat['x']
                    y = heat['y']
                    value = heat['id']
                    data = Heatmaps(x, y, value, 'scroll', event=heat['source'], session_id=session, timeOffset=None , event_info=heat['source'])
                    db.session.add(data)
    db.session.commit()
    return session


def send_email(subject, sender, recipients, text_body, html_body,
               attachments=None, sync=False):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)
    if sync:
        mail.send(msg)
    else:
        Thread(target=send_async_email,
            args=(app._get_current_object(), msg)).start()
