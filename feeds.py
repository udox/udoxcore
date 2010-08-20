from datetime import datetime
from django.contrib.syndication.feeds import Feed
from django.core import urlresolvers
from django.conf import settings
from django.contrib.comments.models import Comment
from django.db.models import get_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.syndication.feeds import FeedDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sites.models import Site


class SpineTV_BaseFeed(Feed):
    author_name = 'SpineTV'
    author_email = 'info@spinetv.com'
    copyright = 'Copyright &copy; %s, SpineTV.com' % datetime.now().year
    max_items = settings.FEEDS_MAX_ITEMS

    
class RecentComments(SpineTV_BaseFeed):
    
    def get_object(self, bits):
        content_type = None
        object_pk = None
        if len(bits) > 0:
            app, model = bits[0].split('.')
            content_type = ContentType.objects.get(app_label=app, model=model)
            if len(bits) > 1:
                object_pk = bits[1]
        return {'content_type':content_type, 'object_pk':object_pk}
    
    def items(self, obj):
        comments = Comment.objects.all()
        if obj['content_type']:
            comments = comments.filter(content_type__app_label=obj['content_type'].app_label, content_type__model=obj['content_type'].model)
            if obj['object_pk']:
                comments = comments.filter(object_pk=obj['object_pk'])
        return comments.order_by('-submit_date')[:self.max_items]
    
    def title(self, obj):
        if obj['content_type'] is not None:
            if obj['object_pk'] is not None:
                item = obj['content_type'].get_object_for_this_type(pk=obj['object_pk'])
                return "SpineTV.com: Recent Comments: %s: %s" % (obj['content_type'].model_class()._meta.verbose_name_plural.title(), str(item).title())
            else:
                return "SpineTV.com: Recent Comments: %s" % obj['content_type'].model_class()._meta.verbose_name_plural.title()
        else:
            return "SpineTV.com: Recent Comments"
    
    def description(self, obj):
        if obj['content_type'] is not None:
            if obj['object_pk'] is not None:
                item = obj['content_type'].get_object_for_this_type(pk=obj['object_pk'])
                return "Recent comments on %s: %s" % (obj['content_type'].model_class()._meta.verbose_name_plural.title(), str(item).title())
            else:
                return "Recent comments on %s" % obj['content_type'].model_class()._meta.verbose_name_plural.title()
        else:
            return "All the recent comments posted on Spine TV!"

    def link(self, obj):
        url = urlresolvers.reverse('home')
        if obj['content_type'] is not None:
            if obj['object_pk'] is not None:
                item = obj['content_type'].get_object_for_this_type(pk=obj['object_pk'])
                url = item.get_absolute_url()
        return url
    
    def item_link(self, item):
        return item.content_object.get_absolute_url()
    
    def item_guid(self, item):
        return item.get_absolute_url()
        
    def item_author_name(self, item):
        return item.user_name
    
    def item_author_link(self, item):
        return item.user_url
    
    def item_pubdate(self, item):
        return item.submit_date


