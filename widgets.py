from django import forms
from django.conf import settings
from django.db import models
from django.forms.util import flatatt
from django.utils import simplejson
from django.utils.safestring import mark_safe
from django.utils.html import escape, conditional_escape
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _
from django.contrib.admin.templatetags.admin_list import _boolean_icon

# depends on # http://code.google.com/p/django-tagging/
from tagging.models import Tag


# SEE: http://jannisleidel.com/2008/11/autocomplete-widget-for-django-tagging-form-fields/
class AutoCompleteTagInput(forms.TextInput):
    class Media:
        css = {
            'all': (settings.ADMIN_MEDIA_PREFIX + 'css/jquery.autocomplete.css',)
        }
        js = (
            settings.MEDIA_URL + 'js/jquery-1.3.2.min.js',
            settings.ADMIN_MEDIA_PREFIX + 'js/jquery.bgiframe.pack.js',
            settings.ADMIN_MEDIA_PREFIX + 'js/jquery.ajaxQueue.js',
            settings.ADMIN_MEDIA_PREFIX + 'js/jquery.autocomplete.pack.js'
        )

    def render(self, name, value, attrs=None):
        output = super(AutoCompleteTagInput, self).render(name, value, attrs)
        page_tags = Tag.objects.all()
        tag_list = simplejson.dumps([tag.name for tag in page_tags],
                                    ensure_ascii=False)
        return output + mark_safe(u'''<script type="text/javascript">
            jQuery("#id_%s").autocomplete(%s, {
                width: 150,
                max: 10,
                highlight: false,
                multiple: true,
                multipleSeparator: ", ",
                scroll: true,
                scrollHeight: 300,
                matchContains: true,
                autoFill: true,
            });
            </script>''' % (name, tag_list))
        

# from: http://bitbucket.org/stephrdev/django-readonlywidget/
# (PaulG: had to add the "get_positiveintegerfield_value" method)
class ReadOnlyWidget(forms.HiddenInput):
    def __init__(self, db_field, *args, **kwargs):
        self.db_field = db_field
        super(ReadOnlyWidget, self).__init__()

    def render(self, *args, **kwargs):
        field_name, value = args
        field_type = self.db_field.__class__.__name__
        field_value = super(ReadOnlyWidget, self).render(*args, **kwargs)
        output = value

        if hasattr(self, 'get_%s_value' % field_type.lower()):
            try:
                func = getattr(self, 'get_%s_value' % field_type.lower())
                output = func(field_name, value)
            except Exception,e:
                output = e
        else:
            raise AttributeError('%s is not supported by ReadOnlyWidget.' % field_type)
        
        return self.render_output(field_name, field_value, output)

    def render_output(self, field_name, field_value, output):
        return mark_safe('%s %s' % (output, field_value))

    def get_textfield_value(self, field_name, value):
        return '<p style="clear:both;">%s</p>' % value

    def get_charfield_value(self, field_name, value):
        if self.db_field.choices:
            for choice in self.field.choices:
                if value == choice[0]:
                    return conditional_escape(force_unicode(choice[1]))
        else:
            return escape(value)

    def get_positiveintegerfield_value(self, field_name, value):
        return '%d' % value

    def get_integerfield_value(self, field_name, value):
        return '%d' % value

    def get_booleanfield_value(self, field_name, value):
        return _boolean_icon(value)

    def get_filefield_value(self, field_name, value):
        if value:
            return '%s <a target="_blank" href="%s">%s</a>' % (_('Currently:'), value.url, value.name)
        else:
            return ''

    def get_imagefield_value(self, field_name, value):
        return self.get_filefield_value(field_name, value)

    def get_foreignkey_value(self, field_name, value):
        try:
            obj = self.db_field.rel.to.objects.get(**{self.db_field.rel.get_related_field().name: value})
            return '<strong>%s</strong>' % unicode(obj)
        except:
            return ''

    def get_manytomanyfield_value(self, field_name, value):
        output = ['<ul class="m2m_list_%s">' % field_name,]
        for id in value:
            output.append('<li>%s</li>' % unicode(self.db_field.rel.to.objects.get(pk=id)))
        output.append('</ul>')

        return ''.join(output)

    def get_datetimefield_value(self, field_name, value):
        if value:
            return value.strftime('%x %X')
        else:
            return ''

    def get_datefield_value(self, field_name, value):
        if value:
            return value.strftime('%x')
        else:
            return ''


"""
# see http://lazypython.blogspot.com/2008/12/building-read-only-field-in-django.html
# works like this, though a bit ugly inheriting off FileField:
class ReadOnlyWidget(forms.Widget):
    def render(self, name, value, attrs):
        final_attrs = self.build_attrs(attrs, name=name)
        if hasattr(self, 'initial'):
            value = self.initial
        return mark_safe("<p %s>%s</p>" % (flatatt(final_attrs), value or ''))
    
    def _has_changed(self, initial, data):
        return False

class ReadOnlyField(forms.FileField):
    widget = ReadOnlyWidget
    def __init__(self, widget=None, label=None, initial=None, help_text=None):
        forms.Field.__init__(self, label=label, initial=initial, 
            help_text=help_text, widget=widget)
    
    def clean(self, value, initial):
        self.widget.initial = initial
        return initial
"""