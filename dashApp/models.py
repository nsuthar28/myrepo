from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

# Create your models here.


class StripeCustomer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripeCustomerId = models.CharField(max_length=255)
    customer_point = models.PositiveIntegerField(default=5)
    
    def __str__(self):
        return self.user.username

    

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        customer = StripeCustomer.objects.create(user=instance)
        customer.save()
