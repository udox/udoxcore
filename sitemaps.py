from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

class CoreSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return [
            {
                'loc': reverse('home'),
                'changefreq': 'daily',
                'priority': '1',
            },
            {
                'loc': reverse('live_tv'),
                'changefreq': 'never',
                'priority': '0.4',
            },
            {
                'loc': reverse('terms'),
                'changefreq': 'never',
                'priority': '0.1',
            },
            {
                'loc': reverse('privacy'),
                'changefreq': 'never',
                'priority': '0.1',
            },
            {
                'loc': reverse('contact'),
                'changefreq': 'never',
                'priority': '0.1',
            },
        ]
    
    def location(self, obj):
        return obj['loc'] # required - let error happen if not present
    
    def changefreq(self, obj):
        if 'changefreq' in obj:
            return obj['changefreq']
        else:
            return 'never'
    
    def lastmod(self, obj):
        if 'lastmod' in obj:
            return obj['lastmod']
        else:
            return None
    
    def priority(self, obj):
        if 'priority' in obj:
            return obj['priority']
        else:
            return '0.5'
