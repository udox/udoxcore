from datetime import datetime

from django.db import models
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.comments.moderation import CommentModerator, moderator
from django.contrib.comments.models import Comment
from django.db.models.signals import pre_save, post_save, post_delete

# depends on # http://code.google.com/p/django-tagging/
from tagging.fields import Tag, TagField

from udoxcore.utils.antispam import AntispamModerator
from udoxcore.utils.html import sanitize

tag_field_help_text = 'Separate tags with commas. If you want to make a multi-word tag, put quote marks around it eg "Crooked Tongues".'
slug_field_help_text = 'This is the text used in url links for this item. Must be unique.'

GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
)

PUB_STATUS = (
    (0, 'Draft'),
    (1, 'Published'),
    (2, 'Coming Soon'), # a special case of published (just for magazine issues)
)

class NoPrimaryKeyError(Exception):
    pass
    
class BaseManager(models.Manager):
    def from_dict(self, object):
        id_field = 'pk'
        if not id_field in object:
            id_field = 'id'
            if not id_field in object:
                raise NoPrimaryKeyError("Passed object %s has no 'pk' or 'id' key.")
        
        return self.get(id=object[id_field])
    
class BaseModel(models.Model):
    """
    all our models should inherit off this one
    """
    objects = BaseManager()
    class Meta:
        abstract = True
    
def interrogate(item):
    import inspect
    attrs = inspect.getmembers(item)
    output = ''
    for attr, val in attrs:
        output += '%s: %s\n' % (attr, val)
    return output

class StatusManager(BaseManager):
    """
    all models which use the 'status' field should have
    a manager which inherits off this one, so as to retrieve
    only 'published' items by default
    
    if pub_date_field is specified on the model then 'published'
    items won't show until their pub_date arrives
    """
    def get_query_set(self):
        live_statuses = getattr(self.model, 'live_statuses')
        qs = super(StatusManager, self).get_query_set().filter(status__in=live_statuses)
        pub_date_field = getattr(self.model, 'pub_date_field')
        if pub_date_field:
            # jump through some hoops here for the sake of inherited model fields
            field = None
            for i, val in enumerate(self.model._meta.fields):
                if val.attname == pub_date_field:
                    field = val
                    break
            if field:
                # Filter in the SQL, as otherwise datetime.now is cached in the QuerySet query SQL
                qs = qs.extra(where=['`%s`.`%s` < NOW()' % (field.model._meta.db_table, field.column)])
        return qs

class StatusModel(BaseModel):
    """
    all managers for models which use the 'status' field should inherit off this one
    """
    objects = BaseManager()
    live_objects = StatusManager()
    
    status = models.IntegerField(choices=PUB_STATUS, default=1)
    
    live_statuses = [1,2]
    pub_date_field = None
    
    class Meta:
        abstract = True

class CommentableModel(models.Model):
    enable_comments = models.BooleanField(default=True)
    comments = generic.GenericRelation(Comment, content_type_field="content_type", object_id_field="object_pk")
    comment_count = models.PositiveIntegerField(default=0, null=False)
    
    class Meta:
        abstract = True

class TaggableModel(models.Model):
    tags = TagField(help_text=tag_field_help_text, blank=True, null=True)
    
    def get_tags(self):
        return Tag.objects.get_for_object(self)
    
    class Meta:
        abstract = True



# -- extra bits for Comments --

# we'll use these signals to update the 'denormalised' comment_count field on the model being commented
def on_comments_save(sender, **kwargs):
    if kwargs['created'] == True:
        kwargs['instance'].content_object.comment_count += 1
        kwargs['instance'].content_object.save()

post_save.connect(on_comments_save, sender=Comment)

def on_comments_delete(sender, **kwargs):
    kwargs['instance'].content_object.comment_count -= 1
    kwargs['instance'].content_object.save()

post_delete.connect(on_comments_delete, sender=Comment)


class DefaultCommentModerator(AntispamModerator):
    enable_field = 'enable_comments'

moderator.register(CommentableModel, DefaultCommentModerator)


# this one sanitizes comment input for html
def sanitize_comment(sender, instance, **kwargs):
    instance.comment = sanitize(instance.comment, settings.COMMENTS_ALLOWED_TAGS)

pre_save.connect(sanitize_comment, sender=Comment)

# -- /extra bits for Comments --

