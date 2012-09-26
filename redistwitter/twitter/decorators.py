from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse


def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('uid', None):
            return HttpResponseRedirect(reverse("twitter_auth"))
        return view_func(request, *args, **kwargs)
    return wrapper
