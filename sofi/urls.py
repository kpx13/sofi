# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from filebrowser.sites import site
admin.autodiscover()

import settings
import views

urlpatterns = patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    url(r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/static/favicon.ico'}),
    
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/filebrowser/', include(site.urls)),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/jsi18n/', 'django.views.i18n.javascript_catalog'),
    url(r'^ckeditor/', include('ckeditor.urls')),

    url(r'^$' , views.home_page),
    url(r'^archives$' , views.archives_page),
    url(r'^archives/(?P<tag>\w+)$' , views.archives_page),
    url(r'^calendar$' , views.calendar_page),
    url(r'^calendar/(?P<cur_date>[0-9.]+)$' , views.calendar_page),
    url(r'^(?P<page_name>\w+)$' , views.other_page),
    
)
