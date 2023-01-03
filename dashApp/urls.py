from django.urls import path
from . import views
from dashApp.dash_apps.finished_apps import dashboard

urlpatterns = [
    path('', views.home, name='home'),

    # AUTHENTICATION URLS
    path('logout/', views.handlelogout, name='logout'),
    path('signup/', views.handleSignUp, name='signup'),
    path('login/', views.handleLogIn, name='login'),

    # DASHBOARD 
    path('forecast-dashboard/', views.dashboard, name='dashboard'),

    # stripe subscription
    path("create-checkout-session/<slug:price_id>", views.create_checkout_session),
    path("config/", views.stripe_config),
    path("success/", views.success, name="success"),
    path("cancel/", views.cancel, name="cancel"),
    path("subscription/", views.handleSubscription, name="subscription"),
    # path('webhook/', views.stripe_webhook),
    
    # upload file
    path('upload/', views.handleUpload, name='uploadfile'),
    path('oldForecast/<str:fileName>', views.handleOldForecast, name='oldforecast'),


]