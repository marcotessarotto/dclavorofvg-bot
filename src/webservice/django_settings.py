
# Importa il file di impostazioni src/gfvgbo/settings.py
from django.conf import settings
from src.gfvgbo.secrets import *

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    DB_HOSTNAME
except NameError:
    DB_HOSTNAME = 'localhost'

DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.postgresql_psycopg2',
                    'NAME': DB_NAME,
                    'USER': DB_USERNAME,
                    'PASSWORD': DB_PWD,
                    'HOST': DB_HOSTNAME,
                    'PORT': '5432',
                }
            }

INSTALLED_APPS = [
    'src.backoffice.apps.BackofficeConfig'
]

TIME_ZONE = 'CET'
USE_TZ = True
