# -*- coding: utf-8 -*-

import datetime
from django.core.context_processors import csrf
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from pages.models import Page
from articles.models import Article, ArticleTag

def get_common_context(request):
    c = {}
    c['request_url'] = request.path
    c.update(csrf(request))
    return c

def home_page(request):
    c = get_common_context(request)
    c['request_url'] = 'home'
    c['left_col'], c['right_col'] = Article.get_recent()
    return render_to_response('home.html', c, context_instance=RequestContext(request))

def archives_page(request, tag=None):
    c = get_common_context(request)
    c['left_col'], c['right_col'] = Article.get_by_tag(tag)
    c['tags'] = ArticleTag.objects.all()
    return render_to_response('archives.html', c, context_instance=RequestContext(request))

def calendar_page(request, cur_date=None):
    c = get_common_context(request)
    if cur_date:
        c['date'] = cur_date
        cur_date = datetime.datetime.strptime(cur_date, '%d.%m.%Y').date()
    else:
        cur_date = datetime.datetime.now().date()
        c['date'] = cur_date.strftime('%d.%m.%Y')
    c['left_col'], c['right_col'] = Article.get_by_date(cur_date)
    return render_to_response('calendar.html', c, context_instance=RequestContext(request))

def other_page(request, page_name):
    c = get_common_context(request)
    try:
        c.update(Page.get_page_by_slug(page_name))
        return render_to_response('page.html', c, context_instance=RequestContext(request))
    except:
        raise Http404()
