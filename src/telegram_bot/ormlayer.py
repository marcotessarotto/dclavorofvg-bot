import datetime
import os
import django
from django.utils.timezone import now
from django.core.cache import cache

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_settings")
django.setup()

from src.backoffice.models import *

# https://docs.djangoproject.com/en/2.2/topics/cache/#the-low-level-cache-api
use_cache = True


def _update_user_in_cache(telegram_user):
    if use_cache:
        key_name = "user" + str(telegram_user.user_id)
        cache.set(key_name, telegram_user, timeout=60)


def orm_add_telegram_user(user):
    """ creates a new user, if not existing; returns istance """

    telegram_user = orm_get_telegram_user(user.id)

    if telegram_user is None:  # telegram user has not been registered yet
        new_telegram_user = TelegramUser()
        new_telegram_user.user_id = user.id
        new_telegram_user.username = user.username
        new_telegram_user.first_name = user.first_name
        new_telegram_user.last_name = user.last_name
        new_telegram_user.language_code = user.language_code
        new_telegram_user.save()

        # select all news categories
        for k in Category.objects.all():
            new_telegram_user.categories.add(k)

        new_telegram_user.save()

        _update_user_in_cache(new_telegram_user)
        print("orm_add_telegram_user: new user " + str(new_telegram_user.user_id))

        return new_telegram_user
    else:
        print("orm_add_telegram_user: existing user " + str(telegram_user.user_id))
        return telegram_user


def orm_log_news_sent_to_user(news_item, telegram_user):
    item = NewsItemSentToUser()
    item.telegram_user = telegram_user
    item.news_item = news_item
    item.save()


def orm_add_news_item(content: str, telegram_user: TelegramUser):
    news = NewsItem()

    news.title = 'news da ' + str(telegram_user.username)

    if content.startswith('http'):
        data = content.split()
        news.link = data[0]

        if data[1:] is not None:
            news.text = ' '.join(data[1:])

    else:
        news.text = content

    cat = telegram_user.categories.all()[0]

    news.save()

    if cat is not None:
        news.categories.add(cat)
        news.save()


# def orm_add_news_item(title, text, link):
#     """ Aggiunge un nuovo articolo """
#
#     news_id = ''
#
#     # Seleziona un id casule di 5 cifre
#     # import random
#     # for i in range(5):
#     #     news_id += str(random.randint(0, 9))
#
#     # Se l'id è già preso riprova la selezione casuale
#     # queryset = NewsItem.objects.filter(news_id=news_id)
#     # if len(queryset) != 0:
#     #     orm_add_newsitem(title, text, link)
#
#     news = NewsItem()
#     # news.news_id = news_id
#     news.title = title
#     news.text = text
#     news.link = link
#     news.save()
#
#     print('\nNUOVO ARTICOLO: ' + str(news))
#
#     return news


def _orm_get_news_item(news_id):
    queryset_news = NewsItem.objects.filter(id=news_id)
    news_item = queryset_news[0]
    return news_item


def _orm_get_news_item_cache(news_id):
    cache_key = "news" + news_id

    result = cache.get(cache_key)

    if result is None:
        result = _orm_get_news_item(news_id)
        cache.set(cache_key, result, timeout=60)

    return result


def orm_add_feedback(feed, news_id, telegram_user_id):
    """ Aggiunge un nuovo feedback all'articolo """

    # queryset_news = NewsItem.objects.filter(id=news_id)
    # news = queryset_news[0]
    if use_cache:
        news = _orm_get_news_item_cache(news_id)
    else:
        news = _orm_get_news_item(news_id)

    if feed == '+':
        news.like += 1
    elif feed == '-':
        news.dislike += 1
    news.save()

    print("orm_add_feedback news_id=" + str(news_id) + " telegram_user_id=" + str(telegram_user_id))


def orm_add_comment(text, news_id, telegram_user_id):
    """ Aggiunge un nuovo commento per l'articolo """

    queryset_user = TelegramUser.objects.filter(user_id=int(telegram_user_id))
    user = queryset_user[0]

    print("orm_add_comment id=" + str(news_id) + " user_id=" + str(user.id))

    # https://stackoverflow.com/a/12682379/974287
    Comment.objects.create(user_id=user.id, news_id=news_id, text=text)

    # queryset_news = NewsItem.objects.filter(id=news_id)
    # news = queryset_news[0]
    #
    # queryset_user = TelegramUser.objects.filter(user_id=int(user_id))
    # user = queryset_user[0]
    #
    # comment = Comment()
    # comment.user = user
    # comment.news = news
    # comment.text = text
    # comment.save()


def orm_get_comment(user_id):
    """ Restituisce i commenti di un determinato utente """

    user = TelegramUser.objects.filter(user_id=user_id)[0]
    return Comment.objects.filter(user=user)


def orm_get_telegram_user(telegram_user_id):
    """ Restituisce l'oggetto user associato a un determinato utente; istanza di tipo TelegramUser 
    :rtype: TelegramUser
    """

    def _orm_get_telegram_user():

        queryset_user = TelegramUser.objects.filter(user_id=telegram_user_id)

        if len(queryset_user) == 0:
            res = None
        else:
            res = queryset_user[0]

        return res

    def _orm_get_telegram_user_cache():

        key_name = "user" + str(telegram_user_id)

        res = cache.get(key_name)

        if res is None:
            res = _orm_get_telegram_user()
            cache.set(key_name, res, timeout=60)

        return res

    a = datetime.datetime.now()

    if use_cache:
        result = _orm_get_telegram_user_cache()
    else:
        result = _orm_get_telegram_user()

    # if result is None:
    #     result = orm_add_telegram_user(...)
    #     _update_user_in_cache(result)

    b = datetime.datetime.now()

    c = b - a

    print("orm_get_telegram_user dt=" + str(c.microseconds) + " microseconds")

    return result


def orm_get_user_expected_input(obj) -> str:
    """returns user's next expected input and resets it to 'no input expected'"""
    if obj is None:
        return None

    if hasattr(obj, '__dict__'):
        telegram_user = obj
    else:
        telegram_user = orm_get_telegram_user(obj)

    if telegram_user is not None:
        res = telegram_user.chat_state
        telegram_user.chat_state = '-'
        telegram_user.save()
        _update_user_in_cache(telegram_user)
    else:
        res = None

    print("orm_get_user_expected_input(" + str(obj) + "): " + str(res))

    return res


def orm_set_telegram_user_expected_input(obj, expected_input):
    if obj is None:
        return None

    if hasattr(obj, '__dict__'):
        telegram_user = obj
    else:
        telegram_user = orm_get_telegram_user(obj)

    if telegram_user is not None:
        print("orm_set_user_expected_input: user " + str(telegram_user.user_id) + ", setting chat_state to " + expected_input)
        telegram_user.chat_state = expected_input
        telegram_user.save()
        _update_user_in_cache(telegram_user)


def orm_set_telegram_user_educational_level(telegram_user: TelegramUser, choice: str):

    telegram_user.educational_level = choice
    telegram_user.save()
    _update_user_in_cache(telegram_user)


def orm_store_free_text(message_text, telegram_user):
    user_free_text = UserFreeText()
    user_free_text.text = message_text[:1024]
    user_free_text.telegram_user = telegram_user
    user_free_text.save()


def orm_update_telegram_user(telegram_user: TelegramUser):
    if telegram_user is not None:
        telegram_user.save()
        _update_user_in_cache(telegram_user)


def orm_parse_user_age(telegram_user: TelegramUser, message_text: str):
    try:
        age = int(message_text)

        if age < 0:
            return -1
    except ValueError:
        print("wrong format for age! " + message_text)
        return -1

    telegram_user.age = age
    telegram_user.save()
    _update_user_in_cache(telegram_user)
    print("parse_user_age: age set for user " + str(telegram_user.user_id) + " to " + str(age))

    return age


def orm_change_user_privacy_setting(telegram_user_id, privacy_setting):
    telegram_user = orm_get_telegram_user(telegram_user_id)

    telegram_user.has_accepted_privacy_rules = privacy_setting
    telegram_user.privacy_acceptance_mechanism = 'U'

    if privacy_setting:
        telegram_user.privacy_acceptance_timestamp = now()
    else:
        telegram_user.privacy_acceptance_timestamp = None

    telegram_user.save()

    _update_user_in_cache(telegram_user)


# def orm_change_user_intership_setting(telegram_user_id, intership_setting):
#     telegram_user = orm_get_telegram_user(telegram_user_id)
#
#     telegram_user.receive_intership_information = intership_setting
#
#     telegram_user.save()
#
#     if use_cache:
#         key_name = "user" + str(telegram_user.user_id)
#         cache.set(key_name, telegram_user, timeout=60)


def orm_change_user_custom_setting(telegram_user_id, category_name, category_setting):
    telegram_user = orm_get_telegram_user(telegram_user_id)

    categories = orm_get_categories_valid_command()

    cat = next((cat for cat in categories if cat.name == category_name), None)

    if cat is None:
        return False

    if category_setting:
        telegram_user.categories.add(cat)
    else:
        telegram_user.categories.remove(cat)

    telegram_user.save()

    return True


# def orm_change_user_courses_setting(telegram_user_id, courses_setting):
#     telegram_user = orm_get_telegram_user(telegram_user_id)
#
#     telegram_user.receive_courses_information = courses_setting
#
#     telegram_user.save()
#
#     if use_cache:
#         key_name = "user" + str(telegram_user.user_id)
#         cache.set(key_name, telegram_user, timeout=60)


# def orm_change_user_recruiting_days_setting(telegram_user_id, recruiting_days_setting):
#     telegram_user = orm_get_telegram_user(telegram_user_id)
#
#     telegram_user.receive_recruiting_days_information = recruiting_days_setting
#
#     telegram_user.save()
#
#     if use_cache:
#         key_name = "user" + str(telegram_user.user_id)
#         cache.set(key_name, telegram_user, timeout=60)


def orm_update_user_category_settings(telegram_user, category_key):
    """ Aggiorna le categorie selezionate dall'utente"""

    print("orm_update_user_category_settings category_key=" + str(category_key) + " user_id=" + str(telegram_user.user_id))

    queryset_cat = telegram_user.categories.filter(key=category_key)

    if len(queryset_cat) != 0:  # category is present in user settings, we have to remove it
        cat = queryset_cat[0]
        telegram_user.categories.remove(cat)
        telegram_user.save()
        # cat.save()

        print('RIMOZIONE ' + str(cat))

    else:  # category is not present in user settings, we have to add it
        cat = Category.objects.filter(key=category_key)[0]

        telegram_user.categories.add(cat)
        telegram_user.save()
        # cat.save()

        print('AGGIUNTA ' + str(cat))


def orm_get_all_telegram_users():
    queryset_user = TelegramUser.objects.all()

    return queryset_user


_skip_list = [UI_HELP_COMMAND, UI_START_COMMAND, UI_HELP_COMMAND_ALT, UI_START_COMMAND_ALT, UI_PRIVACY_COMMAND,
                                           UI_ME_COMMAND, UI_DETACH_BOT, UI_RESEND_LAST_NEWS_COMMAND, UI_CHOOSE_CATEGORIES_COMMAND,
                                           UI_DEBUG_COMMAND]


def orm_get_categories_valid_command():
    a = datetime.datetime.now()
    queryset = Category.objects.filter(is_telegram_command=True, custom_telegram_command__isnull=False)\
        .exclude(custom_telegram_command__in=_skip_list)\
        .order_by('key')
    b = datetime.datetime.now()
    c = b - a
    print("orm_get_categories_valid_command dt=" + str(c.microseconds) + " microseconds")
    return queryset


def orm_get_categories():
    a = datetime.datetime.now()
    queryset = Category.objects.all().order_by('key')
    b = datetime.datetime.now()
    c = b - a
    print("orm_get_categories dt=" + str(c.microseconds) + " microseconds")
    return queryset


def orm_lookup_category_by_custom_command(custom_telegram_command):
    queryset = Category.objects.filter(custom_telegram_command=custom_telegram_command)
    if len(queryset) == 0:
        return None
    else:
        return queryset[0]


def orm_get_category_group(group_name: str) -> CategoriesGroup:
    """

    :rtype: CategoriesGroup
    """
    queryset = CategoriesGroup.objects.filter(name=group_name)
    if len(queryset) == 0:
        return None
    else:
        return queryset[0]


def orm_inc_telegram_user_number_received_news_items(telegram_user: TelegramUser):
    telegram_user.number_of_received_news_items = telegram_user.number_of_received_news_items + 1
    telegram_user.save()

    _update_user_in_cache(telegram_user)


def orm_set_telegram_user_categories(telegram_user_id: int, categories: object) -> TelegramUser:
    """assign categories to user.categories (replacing exiting user categories); if categories is None, all user's categories are removed"""

    telegram_user = orm_get_telegram_user(telegram_user_id)

    telegram_user.categories.clear()

    if categories is not None:
        telegram_user.categories.set(categories.all())

    telegram_user.save()
    _update_user_in_cache(telegram_user)

    return telegram_user


def orm_get_last_processed_news():
    now = datetime.datetime.now()

    d = now - datetime.timedelta(days=10)

    news_query = NewsItem.objects.filter(processed=True).filter(processed_timestamp__gte=d).order_by('-processed_timestamp')

    # should check if job offer is still active or not
    return news_query


def orm_get_fresh_news_to_send():
    news_query = NewsItem.objects.filter(processed=False)

    result = []

    if len(news_query) == 0:
        return result

    now = datetime.datetime.now()

    for news in news_query:

        if news.start_publication is not None:
            to_be_processed = news.start_publication <= now
        else:
            to_be_processed = True

        if news.title is None:
            continue

        if not to_be_processed:
            continue

        # to be processed!
        result.append(news)

    return result


def orm_get_system_parameter(param_name):

    def _orm_get_system_parameter(param_name):

        query_result = SystemParameter.objects.filter(name=param_name)

        if len(query_result) == 0:
            return "*** '" + str(param_name) + "' parameter is not defined ***"
        else:
            return query_result[0].value

    def _orm_get_system_parameter_cache(param_name):

        key_name = "syspar" + param_name

        result = cache.get(key_name)

        if result is None:
            result = _orm_get_system_parameter(param_name)
            cache.set(key_name, result, timeout=60)

        return result

    a = datetime.datetime.now()

    if use_cache:
        result = _orm_get_system_parameter_cache(param_name)
    else:
        result = _orm_get_system_parameter(param_name)

    b = datetime.datetime.now()

    c = b - a

    print("orm_get_system_parameter - dt=" + str(c.microseconds) + " microseconds")

    return result

