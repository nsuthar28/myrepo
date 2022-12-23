from django.contrib import admin
from dashApp.models import StripeCustomer, Product, Price 

admin.site.register(StripeCustomer)
admin.site.register(Product)
admin.site.register(Price)
