from django.conf.urls import patterns, url

urlpatterns = patterns('redistwitter.twitter.views',
    url(r'^$', 'index', name="twitter_home"),
    url(r'^auth/$', 'auth', name="twitter_auth"),
    url(r'^register/$', 'register', name="twitter_register"),
    url(r'^login/$', 'login', name="twitter_login"),
    url(r'^logout/$', 'logout', name="twitter_logout"),
    url(r'^u/(?P<username>\w+)/$', 'user_page', name="twitter_user_page"),
    url(r'^follow/(?P<username>\w+)/$', 'follow', name="twitter_follow"),
    url(r'^unfollow/(?P<username>\w+)/$', 'unfollow', name="twitter_unfollow"),
)
