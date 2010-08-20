from urllib2 import urlopen
from xml.etree import ElementTree
#from elementtree import ElementTree # for Python <= 2.4

from django.conf import settings
from django.core.cache import cache

def on_air():
    def from_api():
        # any errors at all will fail silently and return False
        val = False
        try:
            response = urlopen('http://api.ustream.tv/xml/stream/recent/search/username:eq:%s?key=%s' % (settings.USTREAM_USERNAME, settings.USTREAM_API_KEY))
            shows = ElementTree.XML(response.read()).find('results').getchildren()
            val = (len(shows) > 0)
        except:
            pass
        cache.set('ustream_on_air', val, settings.USTREAM_CACHE_TTL)
        return val

    return cache.get('ustream_on_air', from_api())
   
