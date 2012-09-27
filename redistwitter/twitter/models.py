import uuid
import redis

from django.core.urlresolvers import reverse
from django.contrib.auth.hashers import check_password, make_password
from django.utils.encoding import smart_str
from django.utils.http import int_to_base36
from django.utils.timezone import now
from utils import get_relative_time

r = redis.StrictRedis()

class User(object):
    @staticmethod
    def get_user_url(username="", uid=""):
        if not username:
            username = r.get('uid:%s:username' % uid)
        return reverse("twitter_user_page", kwargs={'username': username})

    @staticmethod
    def exists(uid="", username=""):
        if uid:
            return r.get('uid:%s:username' % uid)
        if username:
            return r.get('username:%s:uid' % username)
        return False

    @staticmethod
    def follow_user(from_uid, username="", uid=""):
        if not uid:
            uid = r.get('username:%s:uid' % username)
        if str(from_uid) == str(uid):
            return
        r.sadd('uid:%s:following' % from_uid, uid)
        r.sadd('uid:%s:followers' % uid, from_uid)

    @staticmethod
    def unfollow_user(from_uid, username="", uid=""):
        if not uid:
            uid = r.get('username:%s:uid' % username)
        if str(from_uid) == str(uid):
            return
        r.srem('uid:%s:following' % from_uid, uid)
        r.srem('uid:%s:followers' % uid, from_uid)

    @staticmethod
    def is_following(from_uid, username="", uid=""):
        if not uid:
            uid = r.get('username:%s:uid' % username)
        return r.sismember('uid:%s:following' % from_uid, uid)

    @staticmethod
    def create_user(username, password):
        if r.get('username:%s:uid' % username):
            return "User with this name already exists"
        uid = r.incr('global:nextUserId')
        r.set('uid:%d:username' % uid, username)
        r.set('uid:%d:password' % uid, make_password(password))
        r.set('username:%s:uid' % username, uid)
        r.set('uid:%d:joined' % uid, now().strftime("%Y-%m-%d"))
        return True

    @staticmethod
    def login_user(request, username, password):
        if not r.get('username:%s:uid' % username):
            return "Sorry, but user does not exist"
        uid = int(r.get('username:%s:uid' % username))
        if not check_password(password, r.get('uid:%d:password' % uid)):
            return "Sorry, but username/password does not match"
        auth = r.get('uid:%d:auth' % uid)
        if not auth:
            auth = str(uuid.uuid4()).replace('-', '')[:20]
            r.set('uid:%d:auth' % uid, auth)
            r.set('auth:%s' % auth, uid)
        request.session["uid"] = uid
        request.session["username"] = username
        return True

    @staticmethod
    def logout_user(request, username):
        del request.session["uid"]
        del request.session["username"]
        return True

def get_post_url(pid):
    return reverse("twitter_post", kwargs={'pid': pid})

class Tweet(object):
    @staticmethod
    def create_post(text, uid):
        pids = r.lrange('uid:%s:posts' % uid, 0, 0)
        if pids:
            post = r.get('post:%s' % pids[0])
            if (smart_str('|'.join(post.split('|')[2:])) == smart_str(text)):
                return "No reduplicated message"

        pid = r.incr('global:nextPostId')
        now_time = now().strftime("%Y-%m-%d %H:%M:%S")
        r.set('post:%d' % pid, '%s|%s|%s' % (uid, now_time, text))
        r.lpush('uid:%s:posts' % uid, pid)
        followers = r.smembers('uid:%s:followers' % uid) or []
        for uid in list(followers) + [uid]:
            r.lpush('uid:%s:timeline' % uid, pid)
        # push it on the timeline
        r.lpush('global:timeline', pid)
        r.ltrim('global:timeline', 0, 100)
        return True

    @staticmethod
    def get_posts(uid="", username="", index=0):
        if not uid:
            uid = r.get('username:%s:uid' % username)
        pid_list = r.lrange('uid:%s:posts' % uid, index, 19) or []
        result = []
        for pid in pid_list:
            post = r.get('post:%s' % pid)
            item = {
                'added': get_relative_time(post.split('|')[1]),
                'text': '|'.join(post.split('|')[2:]),
                'url': get_post_url(pid),
            }
            result.append(item)
        return result

    @staticmethod
    def get_timeline(uid):
        pid_list = r.lrange('uid:%s:timeline' % uid, 0, 100) or []
        result = []
        for pid in pid_list:
            post = r.get('post:%s' % pid)
            item = {
                'added': get_relative_time(post.split('|')[1]),
                'username': r.get('uid:%s:username' % post.split('|')[0]),
                'text': '|'.join(post.split('|')[2:]),
                'url': get_post_url(pid),
            }
            result.append(item)
        return result

    @staticmethod
    def get_post(pid):
        post = r.get('post:%s' % pid)
        item = {
            'added': get_relative_time(post.split('|')[1]),
            'text': '|'.join(post.split('|')[2:]),
            'username': r.get('uid:%s:username' % post.split('|')[0]),
        }
        return item

