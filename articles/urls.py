from django.conf.urls.defaults import patterns, url
from views import news


urlpatterns = patterns('catalog.views',
        url(r'^$', news,  name="news"),
    )
