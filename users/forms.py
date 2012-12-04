# -*- coding: utf-8 -*-
 
from django.forms import ModelForm
from django.contrib.auth.models import User
from django import forms
from models import UserProfile
 
class ProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ('phone', 'work_phone', 'qiwi')

class UserForm(ModelForm):
    passwd1 = forms.CharField(label=u'Пароль', widget=forms.PasswordInput)
    passwd2 = forms.CharField(label=u'Повторите пароль', widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ('first_name', 'email', 'passwd1', 'passwd2')