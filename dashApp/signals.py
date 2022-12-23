from django.dispatch import Signal, receiver
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from functools import wraps

state_change = Signal(providing_args=["state"])

@receiver(state_change)
def set_state(sender,  **kwargs):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        state = kwargs["state"]
        request = kwargs["request"]
        print("in updated signal...................................", kwargs)
        if kwargs["state"] == 'trial_end':
            return HttpResponse("hello signals.......")
        elif kwargs["state"] == "cancelled":
            print("cancel signal......")
            logout(request)
            print("out.")
            return HttpResponseRedirect('/home/') 
        else:
            print(request, args, kwargs)
            return function(request, *args, **kwargs)
            

    return wrap