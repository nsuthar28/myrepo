from django.contrib import admin
from dashApp.models import StripeCustomer, CustomerData

admin.site.register(StripeCustomer)
admin.site.register(CustomerData)