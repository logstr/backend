from datetime import timedelta
from flask_rq2 import RQ

rq = RQ()


@rq.job
def add(x, y):
    return x + y

@rq.job
def mul(x, y, timeout='20'):
    return x * y
