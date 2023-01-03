from .models import *

def access_banner_image(request):
    """The context processor must return a dictionary."""
    try:
        stripeuser = StripeCustomer.objects.get(user= request.user)
        return {'point': stripeuser.customer_point}
    except:
        return {'point': 0} 