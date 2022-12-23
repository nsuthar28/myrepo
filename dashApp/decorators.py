from functools import wraps
from django.http import HttpResponseRedirect
from dashApp.models import *
from django.shortcuts import render,redirect
import datetime

# def login_required(funct)
def subscribers_only(function):
  @wraps(function)
  def wrap(request, *args, **kwargs):
        user = StripeCustomer.objects.get(user=request.user)
        print("user",user,user.is_subscribed)
        
        trial_end = False
        subscription_end = False
        if user.trial_end != None:
            
            if user.trial_end.date() >= datetime.datetime.now().date():
                trial_end = True
        if user.subscription_end != None:
            if user.subscription_end.date() >= datetime.datetime.now().date():
                subscription_end = True    
        
        print("trial_end", trial_end)
        print("subscription_end", subscription_end)
        if user.is_subscribed and (trial_end or subscription_end):
            print(request, args, kwargs)
            return function(request, *args, **kwargs)  
        else:
            return HttpResponseRedirect('/subscription/')

  return wrap
