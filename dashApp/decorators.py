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
        
        if user.customer_point >= 1:
            return function(request, *args, **kwargs)  
        else:
            return HttpResponseRedirect('/subscription/')

  return wrap


