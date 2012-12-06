# -*- coding: utf-8 -*-
from django.db import models
from ckeditor.fields import RichTextField
from taggit.managers import TaggableManager
from taggit.models import Tag, TaggedItem

class ArticleTag(Tag):
    class Meta:
        proxy = True

    def slugify(self, tag, i=None):
        slug = tag.lower().replace(' ', '-')
        if i is not None:
            slug += '-%d' % i
        return slug

class ArticleTaggedItem(TaggedItem):
    class Meta:
        proxy = True

    @classmethod
    def tag_model(cls):
        return ArticleTag

class Article(models.Model):
    name = models.CharField(max_length=128, verbose_name=u'название')
    date = models.DateField(verbose_name=u'дата')
    text = RichTextField(verbose_name=u'текст')
    tags = TaggableManager(through=ArticleTaggedItem)
   
    class Meta:
        verbose_name = u'статья'
        verbose_name_plural = u'статьи'
        ordering = ['-date']
    
    def __unicode__(self):
        return self.name
    
    @staticmethod
    def get_recent(count=4):
        articles = list(Article.objects.all()[:count])
        num = len(articles)
        left_num = num - num / 2
        return (articles[:left_num], articles[left_num:])
    
    @staticmethod
    def get_by_tag(tag=None):
        if not tag:
            return ([], [])
        else:
            articles = list(Article.objects.filter(tags__slug__in=[tag]))
            num = len(articles)
            left_num = num - num / 2
            return (articles[:left_num], articles[left_num:])
        
    @staticmethod
    def get_by_date(date=None):
        if not date:
            return Article.get_recent()
        else:
            articles = list(Article.objects.filter(date=date))
            num = len(articles)
            left_num = num - num / 2
            return (articles[:left_num], articles[left_num:])