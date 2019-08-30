
from django.conf import settings

from gfvgbo.gfvgbo.secrets import *

settings.configure(
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': DB_NAME,
            'USER': DB_USERNAME,
            'PASSWORD': DB_PWD,
            'HOST': 'localhost',
            'PORT': '',
        }
    },
    INSTALLED_APPS=[
        'data.apps.DataConfig',
        #'gfvgbo.backoffice.apps.BackofficeConfig'

    ]
)