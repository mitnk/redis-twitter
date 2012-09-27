import json
from datetime import datetime
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.utils.timezone import now, utc

def get_relative_time(t):
    if isinstance(t, basestring):
        t = datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
    delta = (now() - t.replace(tzinfo=utc)).total_seconds()

    if delta < 60:
        return '%d sec ago' % (delta)
    elif delta < 60 * 60:
        return '%d min ago' % (delta / 60)
    elif delta < 60 * 60 * 24:
        return '%d hours ago' % (delta / (60 * 60))
    else:
        return '%d days ago' % (delta / (60 * 60 * 24))

