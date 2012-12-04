# -*- coding: utf-8 -*-
from django.db import models

class Article(models.Model):
    name = models.CharField(max_length=128, verbose_name=u'название')
    date = models.DateField(verbose_name=u'дата')
    text = models.TextField(verbose_name=u'текст')
   
    class Meta:
        verbose_name = u'новость'
        verbose_name_plural = u'новости'
        ordering = ['-date']
    
    def __unicode__(self):
        return self.name