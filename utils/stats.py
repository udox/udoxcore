import datetime

from django.conf import settings
from django.core.cache import cache

# depends on http://github.com/clintecker/python-googleanalytics
from googleanalytics.connection import GAConnection as Connection

# To test queries on the api directly
# http://code.google.com/intl/en/apis/analytics/docs/gdata/gdataExplorer.html

def get_top_videos(max=10):
    def live_results(max):
        connection = Connection(settings.GOOGLE_LOGIN, settings.GOOGLE_PASSWORD)
        account = connection.get_account(settings.GOOGLE_ANALYTICS_ACCOUNT)
        
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=settings.STATS_PERIOD)
        
        data = account.get_data(
            start_date=start_date,
            end_date=end_date,
            dimensions=['pagePath',],
            metrics=['pageviews',],
            sort=['-pageviews',],
            filters=[('pagepath', '=~', '^/video/.+',)],  # change this regex to include magazine eps
            max_results=max
        )
        cache.set('googleanalytics_top_videos', data.list, settings.STATS_CACHE_TTL)
        return data.list
    return cache.get('googleanalytics_top_videos', live_results(max))

