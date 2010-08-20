"""
for this to work you need:
http://www.voidspace.org.uk/downloads/akismet.py
on your PYTHON_PATH

code below is from:
http://sciyoshi.com/blog/2009/jul/17/prevent-django-newcomments-spam-akismet-reloaded/
"""

from django.contrib.comments.moderation import CommentModerator, moderator
from django.contrib.sites.models import Site
from django.conf import settings

class AntispamModerator(CommentModerator):
    def check_spam(self, request, comment, key, blog_url=None, base_url=None):
        try:
            from akismet import Akismet
        except:
            return False

        if blog_url is None:
            blog_url = 'http://%s/' % Site.objects.get_current().domain
            
        ak = Akismet(
            key=key,
            blog_url=blog_url
        )

        if base_url is not None:
            ak.baseurl = base_url

        if ak.verify_key():
            data = {
                'user_ip': request.META.get('REMOTE_ADDR', '127.0.0.1'),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'referrer': request.META.get('HTTP_REFERER', ''),
                'comment_type': 'comment',
                'comment_author': comment.user_name.encode('utf-8'),
            }

            if ak.comment_check(comment.comment.encode('utf-8'), data=data, build_data=True):
                return True

        return False
    
    # change this function name to 'moderate' if you want detected spams to go into moderation instead of being deleted
    def allow(self, comment, content_object, request):
        allow = super(AntispamModerator, self).allow(comment, content_object, request)

        # change this depending on which spam provider you want to use
        spam = self.check_spam(request, comment,
            key=settings.TYPEPAD_ANTISPAM_API_KEY,
            base_url='api.antispam.typepad.com/1.1/'
        )
        #self.check_spam(request, comment,
        #   key=settings.AKISMET_API_KEY,
        #) or 
        
        if settings.DEBUG and spam:
            # so we can see it working!
            comment.comment = 'SPAM! -- %s' % comment.comment
            return True
        else:
            return not spam and allow


