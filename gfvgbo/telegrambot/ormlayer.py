
import os

import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

django.setup()
#############

# from django.contrib.auth.models import User

# Your application specific imports
from data.models import TelegramUser

#from gfvgbo.backoffice.models import TelegramUser


#from gfvgbo.telegrambot.data.models import *

#Add user
# user = User(name="someone", email="someone@example.com")
# user.save()

# Application logic
# first_user = User.objects.all()[0]
#
# print(first_user.name)
# print(first_user.email)

print("list of TelegramUser:")
print(TelegramUser.objects.all())


def orm_add_user(user):
    # {'id': 884401291, 'first_name': 'Marco', 'is_bot': False, 'last_name': 'Tessarotto', 'language_code': 'en'}
    user_id = user.id

    # check if id is present

    #print(TelegramUser.objects.all())

    query_result = TelegramUser.objects.filter(user_id=user.id)

    for item in query_result:
        print(item)

    print(query_result)

    try:
        if len(query_result) == 0:
            obj = TelegramUser()
            obj.user_id = user.id
            obj.first_name = user.first_name
            obj.last_name = user.last_name
            obj.language_code = user.language_code
            obj.save()
            print("TelegramUser added! " + str(obj))
        else:
            print("TelegramUser found: " + str(query_result[0]))
    except TelegramUser.DoesNotExist:
        print("exception TelegramUser.DoesNotExist")
    except RuntimeError:
        print("RuntimeError")
    pass

