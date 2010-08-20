import re
from django.template import defaulttags, VariableDoesNotExist, Node, Variable, TemplateSyntaxError, Library
from django.http import QueryDict

register = Library()


# see: http://www.djangosnippets.org/snippets/1359/

class ResolvingURLNode(defaulttags.URLNode):
    def __init__(self, view_name, args, kwargs, asvar):
        super(ResolvingURLNode, self).__init__(view_name, args, kwargs, asvar)
        
    def render(self, context):
        original_view_name = self.view_name
        try:
            self.view_name = Variable(self.view_name).resolve(context)
        except VariableDoesNotExist:
            pass
        ret = super(ResolvingURLNode, self).render(context)
        # restore view_name in case this node is reused (e.g in a loop) in 
        # which case the variable might resolve to something else in the next iteration)
        self.view_name = original_view_name
        return ret

@register.tag
def resolveurl(parser, token):
    """
    this just replaces the defaulttags.py -> url  tag
    ...to use the different node class above
    
    the idea is that this tag can accept a template variable as the url argument,
    it will resolve this to the view path string normally passed to URLNode
    
    this is *not* resolving the url - just resolving the variable name to the variable value
    
    (could this be done as a decorator to the original function?)
    """
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument"
                                  " (path to a view)" % bits[0])
    viewname = bits[1]
    args = []
    kwargs = {}
    asvar = None

    if len(bits) > 2:
        bits = iter(bits[2:])
        for bit in bits:
            if bit == 'as':
                asvar = bits.next()
                break
            else:
                for arg in bit.split(","):
                    if '=' in arg:
                        k, v = arg.split('=', 1)
                        k = k.strip()
                        kwargs[k] = parser.compile_filter(v)
                    elif arg:
                        args.append(parser.compile_filter(arg))
    return ResolvingURLNode(viewname, args, kwargs, asvar)





# http://andre.liquidmm.com/blog/2009/apr/20/flexible-query-string-building-template-tag/
# ...hacked to allow the code in the {% qs %} block to contain breaks and spaces
# i.e. if you have complicated qs code (wrap the whole thing in {% spaceless %})
def querystring(qsdict, extra=None):
    qs = QueryDict("").copy()
    qs.update(qsdict)
    if extra:
        extra = re.sub('\s', '', extra)
        for bit in extra.split("&"):
            if bit:
                k, v = bit.split("=")
                if v:
                    qs[k] = v
                elif k in qs:
                    del(qs[k])
    # remove pointless click coordinates from image submit buttons
    # (could be a problem if you have legit 'x' and 'y' vars!)
    if 'x' in qs:
        del(qs['x'])
    if 'y' in qs:
        del(qs['y'])
    for k in qs.keys():
        if isinstance(qs[k], bool):
            qs[k] = 1 if qs[k] else 0
        elif qs[k] is None:
            del(qs[k])
    return qs.urlencode()

@register.tag('qs')
def do_qs(parser, token):
    nodelist = parser.parse(('endqs',))
    parser.delete_first_token()
    dicts = token.split_contents()
    del(dicts[0])
    return QSNode(dicts, nodelist)

class QSNode(Node):
    def __init__(self, qdicts, nodelist):
        self.nodelist = nodelist
        self.qdicts = [Variable(qdict) for qdict in qdicts]

    def render(self, context):
        qdicts = [qdict.resolve(context) for qdict in self.qdicts]
        qdict = qdicts.pop(0)
        while qdicts:
            qdict.update(qdicts.pop(0))
        inner = self.nodelist.render(context).strip()
        qs = querystring(qdict, extra=inner)
        if qs:
            qs = "?" + qs
        return qs
