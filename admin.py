from django.conf import settings
from django.contrib import admin
from django.contrib.admin import actions
from django.utils.translation import ugettext_lazy, ugettext as _

# depends on http://github.com/matthiask/feincms/
from feincms.admin import editor

from udoxcore.widgets import ReadOnlyWidget, AutoCompleteTagInput


class StatusModelAdmin(admin.ModelAdmin):
    """
    all our classes which inherit off StatusModel (i.e. use StatusManager)
    should have their admin class inherit from this one
    """
    def queryset(self, request):
        qs = self.model.objects.get_query_set() # <-- our hack
        
        # rest of code below is copy & pasted from django.contrib.admin.options.py
        
        # TODO: this should be handled by some parameter to the ChangeList.
        ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs



class CommentableModelAdmin(admin.ModelAdmin):
    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(CommentableModelAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'comment_count':
            field.widget = ReadOnlyWidget(db_field=db_field)
        return field    


class TaggableModelAdmin(admin.ModelAdmin):
    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(TaggableModelAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'tags':
            field.widget = AutoCompleteTagInput()
        return field    



"""
For this hack to work the django-mptt managers.py has to have been patched:
http://code.google.com/p/django-mptt/issues/detail?id=13

Note that the original patch is not compatible with Python 2.4
(uses a couple of shorthand if statements)
"""
def delete_selected_tree(modeladmin, request, queryset):
    return_val = actions.delete_selected(modeladmin, request, queryset)
    if return_val is None:
        # this means deletion was completed
        tree_manager = getattr(modeladmin.model._meta,'tree_manager_attr','tree')
        tree = getattr(modeladmin.model,tree_manager)
        tree.rebuild()
    return return_val

delete_selected_tree.short_description = ugettext_lazy("Delete selected %(verbose_name_plural)s")

class MPTTModelAdmin(editor.TreeEditor):    
    # see: http://magicrebirth.wordpress.com/2009/08/18/django-admin-and-mptt-2/
    # this extends the method already found in (FeinCMS) TreeEditor class
    def _actions_column(self, obj):
        actions = super(MPTTModelAdmin, self)._actions_column(obj)
        actions.insert(0,
            u'<a href="add/?%s=%s" title="%s"><img src="%simg/admin/icon_addlink.gif" alt="%s" /></a>' % (getattr(self.model._meta,'parent_attr','parent'), obj.pk, 'Add child', settings.ADMIN_MEDIA_PREFIX, _('Add child'))
        )
        actions.insert(0,
            u'<a href="%s" title="%s" target="_blank"><img src="%simg/admin/selector-search.gif" alt="%s" /></a>' % (obj.get_absolute_url(), 'View on site', settings.ADMIN_MEDIA_PREFIX, _('View on site'))
        )
        return actions
    
    def get_actions(self, request):
        actions = super(MPTTModelAdmin, self).get_actions(request)
        actions['delete_selected'] = (delete_selected_tree, 'delete_selected', delete_selected_tree.short_description) # replace the default delete action
        return actions
