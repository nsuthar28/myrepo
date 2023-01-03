"""
Django settings for ForecastDash project.

Generated by 'django-admin startproject' using Django 3.2.16.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-%9d!@%5&%%f4l@*u72f0dajjz#e@_%sl-h+3r!&2v6417teqop'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["*"]


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    "whitenoise.runserver_nostatic",
    'django.contrib.staticfiles',
    'dashApp',
    'django_plotly_dash.apps.DjangoPlotlyDashConfig',
    'channels',
    'channels_redis',
    'dpd_static_support',
    'bootstrap4'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_plotly_dash.middleware.BaseMiddleware',
    'django_plotly_dash.middleware.ExternalRedirectionMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ForecastDash.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ["templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'dashApp.context_processors.access_banner_image'
            ],
        },
    },
]


#  enable the use of frames within HTML documents
X_FRAME_OPTIONS = 'SAMEORIGIN'

WSGI_APPLICATION = 'ForecastDash.wsgi.application'

ASGI_APPLICATION = 'strip.routing.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
if (os.environ.get('DJANGO_ENVIRONMENT') == 'release'):
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'), conn_max_age=600),
    }
    print(DATABASES)
elif (os.environ.get('DJANGO_ENVIRONMENT') == 'development'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            # This is where you put the name of the db file. # If one doesn't exist, it will be created at migration time.    }
            'NAME': 'db.sqlite3',
        }}
    print(DATABASES)
# print("os..",os.environ)

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Authenticate user
AUTHENTICATION_BACKENDS = ['dashApp.auth.CustomEmailAuthBackend.EmailAuthBackend',
                           'django.contrib.auth.backends.ModelBackend',]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

CRISPY_TEMPLATE_PACK = 'bootstrap5'

# Plotly dash settings
PLOTLY_DASH = {
    "ws_route" : "ws/channel",

    # "insert_demo_migrations" : True,  # Insert model instances used by the demo

    "http_poke_enabled" : True, # Flag controlling availability of direct-to-messaging http endpoint

    "view_decorator" : None, # Specify a function to be used to wrap each of the dpd view functions

    "cache_arguments" : True, # True for cache, False for session-based argument propagation

    #"serve_locally" : True, # True to serve assets locally, False to use their unadulterated urls (eg a CDN)

    # "stateless_loader" : "demo.scaffold.stateless_app_loader",
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

# STATIC_ROOT = os.path.join(BASE_DIR,"/static/")
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"
STATIC_URL = '/static/'
if DEBUG:
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'static')
    ]
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')


# Caching - demo uses redis as this is present due to channels use
# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": "redis://127.0.0.1:6379/1",
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient"
#         },
#         # "KEY_PREFIX": "dpd-demo"
#     }
# }

# Channels config, to use channel layers
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379),],
        }
    }
}

# Staticfiles finders for locating dash app assets and related files
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django_plotly_dash.finders.DashAssetFinder',
    'django_plotly_dash.finders.DashComponentFinder',
    'django_plotly_dash.finders.DashAppDirectoryFinder',
]

# django-dash-plotly components
PLOTLY_COMPONENTS = [
    'dash_core_components',
    'dash_html_components',
    'dash_renderer',
    'dpd_components',
    'dpd_static_support'
]


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Media files(csv, xlsx, pdf, etc..)
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = 'media/'

# Stripe api keys
STRIPE_PUBLISHABLE_KEY = os.environ.get(
    "STRIPE_PUBLISHABLE_KEY", 'pk_test_51M2Z01SIZVPMggpPEV2uDqTCJzQAGivEqIAIEaPELKlg8PHd8gd80nZwGg7rQ9sqxc5a8PhLPO3Sr8dv64eAde9c0098cvWOTy')
STRIPE_SECRET_KEY = os.environ.get(
    "STRIPE_SECRET_KEY", 'sk_test_51M2Z01SIZVPMggpPoCiA2fFNTL4kuGFQFCdLwEcBTooaZ6sO6APDPReYNAW7n4kQeml3GIEm3y3dZ3qy1rSxNIhX00Pl87n6h2')
STRIPE_WEBHOOK_SECRET = os.environ.get(
    "STRIPE_WEBHOOK_SECRET", 'whsec_4bcd158ff18b2b334ef8c79172bfe4b03d4a08694757943ee6c649cbd95a10a7')
STRIPE_PLAN_LIMIT = os.environ.get(
    "STRIPE_PLAN_LIMIT", 2)    