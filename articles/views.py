# -*- coding: utf8 -*-
from django.shortcuts import render
from models import Article


def news(request):
    """
    Каталог продукции
    """

    return render(request, 'news.html',
        {
            'news': Article.objects.all()
        }
    )