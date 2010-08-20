from django import template
from django.template.defaultfilters import stringfilter, _js_escapes

register = template.Library() 

# http://w.holeso.me/2008/08/a-simple-django-truncate-filter/
@register.filter("truncate_chars")  
def truncate_chars(value, max_length):
    if len(value) > max_length:
        truncd_val = value[:max_length]
        if not len(value) == max_length+1 and value[max_length+1] != " ":
            truncd_val = truncd_val[:truncd_val.rfind(" ")]
        return  truncd_val + "..."
    return value
truncate_chars.is_safe = True

# inserts linebreaks every x chars regardless of word boundaries
@register.filter("hardwrap")  
def hardwrap(value, line_length):
    val_len = len(value)
    if val_len > line_length:
        offset = val_len % line_length
        # loop backwards so as not to get tripped up by the changing string length
        for i in range(0, val_len, line_length):
            pos = val_len - i - offset
            if pos > 0:
                value = value[:pos] + "\n" + value[pos:]
    return value
hardwrap.is_safe = True


# splits string into a list of strings
@register.filter("split")  
def split(value, sep=None):
    return value.split(sep)
split.is_safe = True


"""
for flowplayer... it seems to take the safe output of escapejs and unescape it,
thus stuffing itself up. this removes problem chars instead of escaping them
"""
@register.filter("makesafe_for_js")  
def makesafe_for_js(value):
    for bad, good in _js_escapes:
        value = value.replace(bad, '')
    return value
makesafe_for_js = stringfilter(makesafe_for_js)
