from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
import pandas as pd

# Create your models here.


class StripeCustomer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripeCustomerId = models.CharField(max_length=255)
    customer_point = models.PositiveIntegerField(default=5)
    
    def __str__(self):
        return self.user.username

    
class CustomerData(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=255, unique=True)
    data = models.JSONField(null=True)

    @classmethod
    def putframe(cls, file_data, user, file):
        # import pdb;pdb.set_trace()
        customerdata = CustomerData.objects.filter(customer=user, file_name=file).first()
        count = 1
        for dataframe in file_data:
            df = pd.read_json(dataframe, orient='split')
            customerdata.data["df_"+str(count)] = df.to_json(orient='split')
            count += 1
            
        print("dataframe.to_json(orient='split')", customerdata.data)
        customerdata.save()
        return customerdata

    def loadframe(self):
        return pd.read_json(self.data, orient='split')



@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        customer = StripeCustomer.objects.create(user=instance)
        customer.customer_point = 5
        customer.save()

        # customer_data = CustomerData.objects.create(customer=instance, data="")
        # customer_data.save()

# @receiver(post_save, sender=StripeCustomer)
# def create_profile(sender, instance, created, **kwargs):
#     if created:
#         import pdb;pdb.set_trace()
#         