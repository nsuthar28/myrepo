import os
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from dashApp.models import *
from dashApp.decorators import subscribers_only

import stripe
import datetime

from django.core.files.storage import FileSystemStorage
import pandas as pd
import json




def handler404(request, exception, template_name="404.html"):
    response = render(request, template_name)
    response.status_code = 404
    return response

def handler500(request, *args, **argv):
    return render(request, '500.html', status=500) 



# Create your views here.
def home(request):
    """ home() will be render landing home page.

    Returns:
       ["home.html] 

    """
    print("home page......")

    return render(request, 'home.html')

@csrf_exempt
@login_required(login_url='/login/')      
@subscribers_only
def dashboard(request, template_name="dashboard.html", *args):
    """ dashboard() will be render dashboard of forcasting.

    Returns:
       ["dashboard.html] 

    """
    print("dashboard......", request)    
    
    fileurl = "./media/Food_Distributor_Data_3items.csv"
    context_data = {"upload-data": {"children": fileurl}}

    context_data_json = json.dumps(context_data)
    print("context_data_json", context_data_json)

    return render(request, "dashboard.html", context={"context": context_data_json})

def handleOldForecast(request, fileName):
    print("handle old forecast")
    import pdb;pdb.set_trace()
    
    customerData = CustomerData.objects.get(customer=request.user, file_name=fileName)
    
    request.session["stored_datas"] = customerData.data
    request.session["is_oldData"] = True
    print("request.session", request.session)

    context_data = {"upload-data": {"children": json.dumps(customerData.data)}}

    context_data_json = json.dumps(context_data)
    print("context_data_json", context_data_json)
    return render(request, "dashboard.html",  context={"context": context_data_json})

@csrf_exempt
def handleSignUp(request):
    """handleSignUp() will register user.

    Requirements:
        [1]: email-ID should be unique.
        [2]: length of password sholud be greater than 5.
        [3]: password and confirm_password should be same.

    Returns:
        [REQUEST-METHOD : POST] : [IF passes all requirements - "login.html"]
                                  [ELSE - "home.html"]
        [REQUEST-METHOD : GET] : [returns "home.html"]
    """ 
    if request.method == 'POST':
        print("request.POST", request.POST)
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        try:
            if User.objects.filter(email=email) != User.objects.filter(email=email).exists(): 
                if len(password) < 5:
                    messages.error(request,"Password too much short")
                    return redirect('signup')
                
                if password != confirm_password:
                    messages.error(request,"Passwords do not match")
                    return redirect('signup')
                myuser = User.objects.create_user(username=username,email=email,password=password)
                myuser.save()
                messages.success(request,"You have successfully Registered")

                print("Registerd..")
                return redirect('login')

        except:
            try:
                if User.objects.filter(email=email).exists():
                    messages.error(request,"Email exists Please Try other Email Address")

                elif User.objects.filter(username=username).exists():
                    messages.error(request,"Username exists Please Try another Username")
                return render(request,'signup.html')
            except:
                pass

        return redirect('home')
    

    return render(request, "signup.html")

@csrf_exempt
def handleLogIn(request):
    """handleLogIn() will authenticate user and log-in user to dashboard.

    Returns:
        [REQUEST-METHOD: POST] : [IF logIn done successfully - ("subscription.html" or "dashboard.html" -> depends on subscription)] 
                                 [ELSE display error message]
        [REQUEST-METHOD: GET] : [return "login.html"]

    """
    if request.method == 'POST':
        print("request.POST", request.POST)
        lemail = request.POST.get('email')
        password = request.POST.get('password')

        try:

            user = authenticate(username=lemail, password=password)
            if user is not None:
                login(request, user)
                stripeuser = StripeCustomer.objects.get(user= request.user)
                request.session['user'] = lemail
                request.session['point'] = stripeuser.customer_point

                messages.info(request, f"You are now logged in as {lemail}.")
                print("logged in..")
                return render(request, 'uploadFile.html')
            else:
                messages.error(request,"Invalid username or password")
        except:
            messages.error(request, "Unable to logIn")

    return render(request, "login.html")   

def handlelogout(request):
    """handlelogout() will log out logged-in user.

    Returns:
        ["login.html"]: [successfully log-out]
        ["hime.html]: [unable to log-out]

    """
    try:
        logout(request)
        return redirect("login")
        # return redirect(handleLogIn)
    except:
        messages.error("Unable to logout")
        return redirect("home")

@csrf_exempt
@login_required(login_url='/login/')   
def handleUpload(request):
    print("request.POST", request.method, request.FILES)
    stripeuser = StripeCustomer.objects.get(user= request.user)

    if request.method == 'POST':
        
        print("request.FILES",request.FILES)
        
        request_file = request.FILES.get("fileinput")
        print("request_file", request_file)
        
        request.session["uploaded_file"] = request_file.name
         

        fs = FileSystemStorage()
        file = fs.save("./"+request.user.username+"/"+request_file.name, request_file)
        
        fileurl = fs.url(file)
        print("fileurl", fileurl)

        df = pd.read_csv("./"+fileurl, index_col='Date', parse_dates=True)
        df_json = df.to_json(orient='split')

        custData, created = CustomerData.objects.get_or_create(customer=request.user, file_name=request_file.name, data={"df_initial": df_json})
        custData.save()

        context_data = {"upload-data": {"children": json.dumps({"df_initial": df_json})}}

        context_data_json = json.dumps(context_data)
        print("context_data_json", context_data_json)
        
        stripeuser.customer_point -= 1
        stripeuser.save()

        return render(request, "dashboard.html", context={"context": context_data_json})

    else:
        customerDatas = CustomerData.objects.filter(customer=request.user).values('file_name') 
        fileNames = []
        if customerDatas:
            for fname in customerDatas:
                fileNames.append(fname["file_name"])

        return render(request, "uploadFile.html", context={"point": stripeuser.customer_point, "files": fileNames})
    

def set_subscription(user):
    try:
        subscriber = StripeCustomer.objects.get(user=user)
        if subscriber:
            subscriber.is_subscribed = True
            subscriber.save()
            print("subscriber", subscriber.is_subscribed)
    except:
        print(f"unable to set is_subscribed for {user}")

@csrf_exempt
@login_required(login_url='/login/')
def stripe_config(request):
    """stripe_config() will handle the AJAX request.

    Returns:
        [JsonResponse]: json of STRIPE_PUBLISHABLE_KEY

    """
    if request.method == "GET":
        stripe_config = {"publicKey": settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=True)

@csrf_exempt
@login_required(login_url='/login/')
def create_checkout_session(request, price_id):
    """create_checkout_session() will send AJAX request to the server to generate a new Checkout Session ID.

    Returns:
        [IF payment success : "success.html"]
        [ELSE payment canceled : "cancel.html"]
    
    """
    if request.method == "GET":
        domain_url = os.environ.get('DOMAIN_URL','http://localhost:8000/')
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe_customer = StripeCustomer.objects.get(user=request.user)
        try:
            checkout_session = stripe.checkout.Session.create(
                client_reference_id = request.user.id if request.user.is_authenticated else None,
                success_url=domain_url + "success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=domain_url + "cancel/",
                payment_method_types= ["card"],
                mode='payment',
                line_items=[
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ],
                
            )
            # set is_subscriptions field of user
            # set_subscription(request.user)
            request.session["price_id"] = price_id
            print('checkout_session',checkout_session)


            return JsonResponse({"sessionId": checkout_session["id"]})


        except Exception as e:
            return JsonResponse({"error": str(e)})

# @login_required(login_url='/login/')
def success(request):
    """success() will render on successfull subscription-payment.
    """
    # print("success...")
    # import pdb;pdb.set_trace()
    price_id = request.session.get("price_id")
    stripe_price = stripe.Price.retrieve(price_id)
    stripe_product = stripe.Product.retrieve(stripe_price.product)
    stripeuser = StripeCustomer.objects.get(user= request.user)
    stripeuser.customer_point += int(stripe_product.metadata.point)
    stripeuser.save()

    return render(request, "success.html")

# @login_required(login_url='/login/')
def cancel(request):
    """cancel() will render on cancellation of subscription-payment.
    """
    return render(request, "cancel.html")            

def handleSubscription(request):
    """handleSubscription() will render pricing plans of all subscriptions.
    """
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe_products = stripe.Product.list(limit=settings.STRIPE_PLAN_LIMIT)
        print("stripe_products", stripe_products)
        stripe_product = []
        for product in stripe_products.data:
            prod = dict()
            prod['description'] = product.description#
            prod['name'] = product.name#
            prod['point'] = product.metadata.point#
            prod['price_id'] = str(product.default_price)
            stripe_price = stripe.Price.retrieve(product.default_price)#
            prod['price'] = float(stripe_price.unit_amount/100)#
            prod['unit'] = stripe_price.currency#
        
            stripe_product.append(prod)
        # stripe_product = sorted(stripe_product, key=lambda x: x['price'])
        context={'data':stripe_product}
        print('context..........', context )
    except Exception as e:
        print(e)
    return render(request, "subscription.html", context)



# @csrf_exempt
# def stripe_webhook(request):
#     print("in webhook...")
#     stripe.api_key = settings.STRIPE_SECRET_KEY
#     endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
#     payload = request.body
#     sig_header = request.META['HTTP_STRIPE_SIGNATURE']
#     event = None

#     try:
#         event = stripe.Webhook.construct_event(
#             payload, sig_header, endpoint_secret
#         )
#     except ValueError as e:
#         # Invalid payload
#         return HttpResponse(status=400)
#     except stripe.error.SignatureVerificationError as e:
#         # Invalid signature
#         return HttpResponse(status=400)
#     print("event type...", event['type'])

#     # Handle the checkout.session.completed event
#     if event['type'] == 'checkout.session.completed':
#         print(event)
#         session = event['data']['object']

#         # Fetch all the required data from session
#         client_reference_id = session.get('client_reference_id')
#         # stripe_customer_id = session.get('customer')
#         # stripe_subscription_id = session.get('subscription')
#         # Get the user and create a new StripeCustomer
#         user = User.objects.get(id=client_reference_id)
#         # get stripe customer object
#         StripeCustomer_object = StripeCustomer.objects.get(user=user)
#         # get stripe subscription object
#         # stripe_subscription_object = stripe.Subscription.retrieve(stripe_subscription_id)
#         # print("stripe_subscription_object", stripe_subscription_object)

#         # stripe_subscription_status = stripe_subscription_object["items"]["data"][0]["plan"]["active"]    
#         # stripe_product_id = stripe_subscription_object["items"]["data"][0]["plan"]["product"]
#         # stripe_subscription_end = stripe_subscription_object['current_period_end']
#         # stripe_trial_end = stripe_subscription_object['trial_end']
#         # set stripe-customer-id and stripe-subsciption-id 
#         # StripeCustomer_object.is_subscribed = stripe_subscription_status
#         # StripeCustomer_object.stripeSubscriptionId=stripe_subscription_id
#         # StripeCustomer_object.stripeCustomerId= stripe_customer_id
#         # StripeCustomer_object.stripeProductId = stripe_product_id
#         # if StripeCustomer_object.subscription_end == None:
#             # StripeCustomer_object.subscription_end = datetime.datetime.fromtimestamp(stripe_subscription_end).date()
#             # StripeCustomer_object.trial_end = datetime.datetime.fromtimestamp(stripe_trial_end).date()
            
#         # else:
#             # t= StripeCustomer_object.subscription_end.date()
#             # s= datetime.datetime.fromtimestamp(stripe_subscription_end).date()
#             # current = datetime.datetime.now().date()
#             # if t < current:
#                     # stripe_subscription_end_final = s
#                     # StripeCustomer_object.subscription_end = stripe_subscription_end_final
                
#             # elif t > current:
#                     # s_days= (s - current).days
#                     # stripe_subscription_end_final = t + datetime.timedelta(days = s_days)
#                     # StripeCustomer_object.subscription_end = stripe_subscription_end_final
            
#         StripeCustomer_object.customer_point += 5 
#         StripeCustomer_object.save()

#         print(user.username + ' just subscribed.')

#     return HttpResponse(status=200)


