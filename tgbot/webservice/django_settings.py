
# Importa il file di impostazioni tgbot/gfvgbo/settings.py
from django.conf import settings
from tgbot.gfvgbo.mysecrets import *

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': DB_NAME,
        'USER': DB_USERNAME,
        'PASSWORD': DB_PWD,
        'HOST': 'localhost',
        'PORT': '3306',
        'AUTOCOMMIT': True,
        'OPTIONS': {'charset': 'utf8mb4',
                    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"},
        # https://code.djangoproject.com/ticket/18392
    }
}

INSTALLED_APPS = [
    'tgbot.backoffice.apps.BackofficeConfig'
]

TIME_ZONE = 'CET'
USE_TZ = True
