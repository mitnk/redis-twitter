from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from models import User

def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        uid = request.session.get('uid', None)
        if not uid or not User.exists(uid=uid):
            if 'uid' in request.session:
                del request.session['uid']
            if 'username' in request.session:
                del request.session['username']
            return HttpResponseRedirect(reverse("twitter_auth"))
        return view_func(request, *args, **kwargs)
    return wrapper
