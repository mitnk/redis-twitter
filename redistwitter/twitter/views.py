from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render

from decorators import login_required
from forms import RegisterForm, LoginForm, TweetForm
from models import User, Tweet


def register(request):
    form = RegisterForm(request.POST)
    if form.is_valid():
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        result = User.create_user(username, password)
        if result is True:
            messages.success(request, "Created Successfully! Please Login")
        elif isinstance(result, basestring):
            messages.error(request, result)
        return HttpResponseRedirect(reverse("twitter_home"))
    context = {
        'register_form': form,
        'login_form': LoginForm(),
    }
    return render(request, "twitter/index.html", context)

def login(request):
    form = LoginForm(request.POST)
    if form.is_valid():
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        result = User.login_user(request, username, password)
        if result is True:
            messages.success(request, "Welcome Back!")
        elif isinstance(result, basestring):
            messages.warning(request, result)
        return HttpResponseRedirect(reverse("twitter_home"))
    context = {
        'register_form': RegisterForm,
        'login_form': form,
    }
    return render(request, "twitter/index.html", context)

def logout(request):
    if request.session.get("uid"):
        User.logout_user(request, request.session['username'])
    return HttpResponseRedirect(reverse("twitter_home"))

def auth(request):
    if request.session.get('uid'):
        return HttpResponseRedirect(reverse("twitter_home"))
    register_form = RegisterForm()
    login_form = LoginForm()
    context = {
        'register_form': register_form,
        'login_form': login_form,
    }
    return render(request, "twitter/auth.html", context)

@login_required
def index(request):
    if request.method == "POST":
        form = TweetForm(request.POST)
        if form.is_valid():
            uid = request.session['uid']
            Tweet.create_post(text=form.cleaned_data["text"], uid=uid)
            return HttpResponseRedirect(reverse("twitter_home"))
    else:
        form = TweetForm()
    context = {
        'username': request.session['username'],
        'tweet_form': form,
        'timeline': Tweet.get_timeline(request.session['uid']),
    }
    return render(request, "twitter/index.html", context)


@login_required
def follow(request, username):
    User.follow_user(request.session['uid'], username=username)
    url = User.get_user_url(username=username)
    return HttpResponseRedirect(url)


@login_required
def unfollow(request, username):
    User.unfollow_user(request.session['uid'], username=username)
    url = User.get_user_url(username=username)
    return HttpResponseRedirect(url)


@login_required
def user_page(request, username):
    if not User.exists(username=username):
        raise Http404()
    posts = Tweet.get_posts(username=username)
    following = User.is_following(request.session['uid'], username=username)
    context = {
        'username': username,
        'posts': posts,
        'followed': following,
        'my_username': request.session['username'],
    }
    return render(request, "twitter/user_page.html", context)

def show_post(request, pid):
    post = Tweet.get_post(pid)
    context = {
        'post': post,
    }
    return render(request, "twitter/show_post.html", context)

