# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from clients.models import Client
from drivers.models import Driver
from operators.models import ExternalOperator, InternalOperator

USER_TYPE = (
             ('s', u'Администратор'),
             ('c', u'Клиент'),
             ('d', u'Водитель'),
             ('io', u'Внутренний оператор'),
             ('eo', u'Внешний оператор')
             )

class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile', verbose_name=u'пользователь')
    phone = models.CharField(max_length=20, verbose_name=u'телефон')
    work_phone = models.CharField(max_length=20, blank=True, verbose_name=u'рабочий телефон')
    qiwi = models.CharField(max_length=20, blank=True, verbose_name=u'Qiwi- кошелек')
    type = models.CharField(max_length=2, default='c', choices=USER_TYPE, verbose_name=u'тип пользователя')
    balance = models.FloatField(default=0.0, verbose_name=u'Баланс')
    
    class Meta:
        verbose_name = 'профиль пользователя'
        verbose_name_plural = 'профили пользователей'
    
    def __unicode__ (self):
        return str(self.user.username)
    
    @property
    def role(self):
        if self.type == 'c':
            if Client.user_is_client(self):
                return Client.get(self.user)
            else:
                raise RuntimeError
        elif self.type == 'd':
            if Driver.user_is_driver(self):
                return Driver.get(self.user)
            else:
                raise RuntimeError
        return None
    
    def pay(self, cost):
        if self.balance > cost:
            self.balance = self.balance - cost
            self.save()
            return True
        else:
            return False
        
    def earn(self, cost):
        self.balance = self.balance + cost
        self.save()
    
    
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)