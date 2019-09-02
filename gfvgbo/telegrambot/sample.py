# main.py
# Django specific settings
import os
import sys

import django

#sys.path.insert(0, os.path.abspath('../../')) # non serve, c'è già

#sys.path.insert(0, os.path.abspath('../backoffice/'))
print(sys.path)
#
# # print(os.path.abspath('.'))
#
# import settings
# print( dir(settings) )




#import gfvgbo.telegrambot.settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

### Have to do this for it to work in 1.9.x!
# from django.core.wsgi import get_wsgi_application
# application = get_wsgi_application()
# settings.configure()

django.setup()
#############

# from django.contrib.auth.models import User

# Your application specific imports
from gfvgbo.backoffice.models import *
#from backoffice.models import TelegramUser

#from gfvgbo.backoffice.models import TelegramUser


#from gfvgbo.telegrambot.backoffice.models import *

#Add user
# user = User(name="someone", email="someone@example.com")
# user.save()

# Application logic
# first_user = User.objects.all()[0]
#
# print(first_user.name)
# print(first_user.email)

print(TelegramUser.objects.all())


query_result = TelegramUser.objects.filter(user_id=12345)

if len(query_result) == 0:
    obj = TelegramUser()
    obj.user_id = 12345
    obj.first_name = "m"
    obj.last_name = "t"
    obj.language_code = "en"
    obj.save()
    print("TelegramUser added! " + str(obj))