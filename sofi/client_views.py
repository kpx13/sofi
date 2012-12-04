# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect, Http404
from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.forms.util import ErrorList
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.http import urlquote
from robokassa.forms import RobokassaForm

from clients.models import Client
from clients.forms import ClientForm
from orders.forms import OrderForm
from orders.models import Order
from users.forms import ProfileForm, UserForm
from views import get_common_context


def client_required(view_function, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """ Декоратор для вьюх, который проверяет, что юзер - клиент """
    
    if not login_url:
        login_url = settings.LOGIN_URL
        
    def wrapped_function(request, *args, **kwargs):
        if request.user.is_authenticated() and Client.user_is_client(request.user):
            return view_function(request, *args, **kwargs)
        else:
            path = urlquote(request.get_full_path())
            tup = login_url, redirect_field_name, path
            return HttpResponseRedirect('%s?%s=%s' % tup)
    
    return wrapped_function


def get_client_context(request):
    c = get_common_context(request)
    c['client'] = c['user_profile'].role
    return c

@client_required
def cabinet(request, page_name):
    c = get_client_context(request)
    if page_name == 'home':
        c['request_url'] = page_name
        return render_to_response('client/cabinet.html', c, context_instance=RequestContext(request))
    elif page_name == 'history':
        return history(request)
    elif page_name == 'new':
        return new_order(request)
    else:
        raise Http404()
    
def new_order(request):
    c = get_client_context(request)
    
    c['map_center'] = '55.76, 37.64'
    c['map_zoom'] = '11'
    
    if request.method == 'GET':
        order_form = OrderForm()
    elif request.method == 'POST':
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            o = order_form.save(commit=False)
            o.set_created(c['client'])
            messages.success(request, u'Ваш заказ успешно добавлен и ожидает оплаты.')
            return HttpResponseRedirect('/cabinet/history')

    c['order_form'] = order_form
    
    return render_to_response('client/new.html', c, context_instance=RequestContext(request))

def history(request):
    c = get_client_context(request)
    
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        order = Order.get_by_id(request.POST.get('id'))
        action = request.POST.get('action')
        if action == 'pay':
            cost = order.cost
            if c['user_profile'].pay(cost):
                order.set_waiting()
                messages.success(request, u'Ваш заказ успешно оплачен.')
            else:
                messages.error(request, u'У Вас недостаточно средств для совершения платежа.')
        elif action == 'del':
            order.delete()
            messages.success(request, u'Заказ удален.')
        elif action == 'close':
            order.set_closed()
            order.handler.person.get_profile().earn(order.cost * 0.9)
            messages.success(request, u'Вы подтвердили выполнение заказа. Спасибо за использование нашего сервиса.')
        return HttpResponseRedirect('/cabinet/history')

    c['orders'] = Order.objects.filter(customer=c['client'])
    return render_to_response('client/history.html', c, context_instance=RequestContext(request))


def reg_page(request):
    c = get_common_context(request)
    
    if request.method == 'GET':
        client_form = ClientForm()
        profile_form = ProfileForm()
        user_form = UserForm()
    elif request.method == 'POST':
        client_form = ClientForm(request.POST)
        profile_form = ProfileForm(request.POST)
        user_form = UserForm(request.POST)
        if request.POST.get('confirm', None) is None:
            user_form.errors['confirm'] = ErrorList([u'Необходимо согласиться с договором.'])
        elif user_form.data['passwd1'] != user_form.data['passwd2']:
            user_form.errors['passwd1'] = ErrorList([u'Пароли не совпадают.'])
        elif not user_form.data['email']:
            user_form.errors['email'] = ErrorList([u'Обязательное поле.'])
        elif client_form.is_valid() and profile_form.is_valid() and user_form.is_valid():
            try:
                u = auth.models.User(username=user_form.data['email'],
                                     email=user_form.data['email'],
                                     first_name=user_form.data['first_name'],
                                     )
                u.save()
                u.set_password(user_form.data['passwd1'])
                u.save()
            except:
                u = None
                user_form.errors['email'] = ErrorList([u'Пользователь с таким email уже существует'])
                
            if u: # user saved, all is right
                p = u.get_profile()
                p.phone = profile_form.data['phone']
                p.work_phone=profile_form.data['work_phone']
                p.qiwi=profile_form.data['qiwi']
                p.user = u
                p.type = 'c'
                p.save()

                Client.add(u, client_form.data['name'])
                user = auth.authenticate(username=user_form.data['email'], password=user_form.data['passwd1'])
                auth.login(request, user)
                messages.success(request, u'Вы успешно зарегистрировались в системе в качестве клиента.')
                return HttpResponseRedirect('/cabinet')
    
    c['client_form'] = client_form
    c['profile_form'] = profile_form
    c['user_form'] = user_form
    
    return render_to_response('client/reg.html', c, context_instance=RequestContext(request))


def profile(request):
    c = get_client_context(request)
    
    if c['client'].legal_entity:
        client_form = ClientForm(initial={'name': c['client'].legal_entity.name})
    profile_form = ProfileForm(instance=c['user_profile'])
    user_form = UserForm(instance=c['user'])
    robokassa_form = RobokassaForm(initial={
               'OutSum': 500,
               'InvId': 13,
               'Desc': u'Описание',
               'Email': 'annkpx@gmail.com',
               # 'IncCurrLabel': '',
               # 'Culture': 'ru'
           })
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'user':
            user_form = UserForm(request.POST, instance=c['user'])
            
            if user_form.data['passwd1'] != user_form.data['passwd2']:
                user_form.errors['passwd1'] = ErrorList([u'Пароли не совпадают.'])
            elif not user_form.data['email']:
                user_form.errors['email'] = ErrorList([u'Обязательное поле.'])
            elif user_form.is_valid():
                try:
                    u = user_form.save()
                    u.set_password(user_form.data['passwd1'])
                    u.save()
                    messages.success(request, u'Учетные данные успешно изменены.')
                    return HttpResponseRedirect('/profile')
                except:
                    u = None
                    user_form.errors['email'] = ErrorList([u'Пользователь с таким email уже существует'])
            
        elif action == 'profile':
            profile_form = ProfileForm(request.POST, instance=c['user_profile'])
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, u'Данные профиля успешно обновлены.')
                return HttpResponseRedirect('/profile')
        
        elif action == 'client':
            client_form = ClientForm(request.POST)
            #if client_form.is_valid():
            #    c = client_form.save()
            le = c['client'].legal_entity
            le.name = client_form.data['name']
            le.save()
            messages.success(request, u'Данные об организации успешно обновлены.')
            return HttpResponseRedirect('/profile')
        
        elif action == 'to_pay':
            pass
            
    
    c['client_form'] = client_form
    c['profile_form'] = profile_form
    c['user_form'] = user_form
    c['robokassa_form'] = robokassa_form
    print c['robokassa_form'] 
    
    
    return render_to_response('client/profile.html', c, context_instance=RequestContext(request))

from robokassa.signals import result_received

def payment_received(sender, **kwargs):
    print kwargs['InvId']
    print kwargs['OutSum']
    print kwargs['extra']['my_param']

result_received.connect(payment_received)