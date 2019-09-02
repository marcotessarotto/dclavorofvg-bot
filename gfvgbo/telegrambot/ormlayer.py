
import os

import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

django.setup()
#############

# from django.contrib.auth.models import User

# Your application specific imports
from gfvgbo.backoffice.models import TelegramUser, Keyword, create_default_keywords_for_user

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

# print("list of TelegramUser:")
# print(TelegramUser.objects.all())


def orm_add_user(user):
    # {'id': 884401291, 'first_name': 'Marco', 'is_bot': False, 'last_name': 'Tessarotto', 'language_code': 'en'}
    user_id = user.id

    # check if id is present

    #print(TelegramUser.objects.all())

    query_result = TelegramUser.objects.filter(user_id=user.id)

    # for item in query_result:
    #     print(item)

    # print(query_result)

    if len(query_result) == 0:
        obj = TelegramUser()
        obj.user_id = user.id
        obj.first_name = user.first_name
        obj.last_name = user.last_name
        obj.language_code = user.language_code
        obj.save()
        print("TelegramUser added! " + str(obj))

        # add all keywords for user
        create_default_keywords_for_user(obj)

        result = obj
    else:
        print("TelegramUser found: " + str(query_result[0]))
        result = query_result[0]

    return result


def update_user_keyword_settings(django_user, scelta):
    queryset = django_user.keywords.filter(key=scelta)

    if len(queryset) != 0:
        k = queryset[0]
        # remove keyword
        django_user.keywords.remove(k)
        django_user.save()
        k.save()
    else:
        # add keyword

        # print("search for keyword " + str(scelta))

        k = Keyword.objects.filter(key=scelta)[0]

        django_user.keywords.add(k)
        django_user.save()
        k.save()

        pass

    pass


def orm_get_user(user_id):
    query_result = TelegramUser.objects.filter(user_id=user_id)

    return query_result[0]
