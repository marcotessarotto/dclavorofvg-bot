
from django.conf import settings

from gfvgbo.gfvgbo.secrets import *

# import sys
# import os
#
# print("telegrambot django settings")
# print(sys.path)
# print(os.path.abspath('.'))

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
    'data.apps.DataConfig',
    # 'gfvgbo.backoffice.apps.BackofficeConfig'

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
#         'data.apps.DataConfig',
#         #'gfvgbo.backoffice.apps.BackofficeConfig'
#
#     ]
# )

