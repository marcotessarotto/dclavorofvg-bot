
from django.conf import settings

from gfvgbo.gfvgbo.secrets import *

import sys
import os
#
print("telegrambot django settings")
print(sys.path)
print(os.path.abspath('.'))

# import gfvgbo.backoffice.apps

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(BASE_DIR)

DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.postgresql_psycopg2',
                    'NAME': DB_NAME,
                    'USER': DB_USERNAME,
                    'PASSWORD': DB_PWD,
                    'HOST': 'localhost',
                    'PORT': '5432',
                }
            }

INSTALLED_APPS = [
    #'backoffice.apps.DataConfig',
    'gfvgbo.backoffice.apps.BackofficeConfig'

]

# settings.configure(
#     DATABASES={
#         'default': {
#             'ENGINE': 'django.db.backends.postgresql_psycopg2',
#             'NAME': DB_NAME,
#             'USER': DB_USERNAME,
#             'PASSWORD': DB_PWD,
#             'HOST': 'localhost',
#             'PORT': '5432',
#         }
#     },
#     INSTALLED_APPS=[
#         'backoffice.apps.DataConfig',
#         #'gfvgbo.backoffice.apps.BackofficeConfig'
#
#     ]
# )

