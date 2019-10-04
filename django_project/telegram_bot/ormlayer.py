import datetime
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_settings")
django.setup()

from django_project.backoffice.models import *

from django.core.cache import cache
# https://docs.djangoproject.com/en/2.2/topics/cache/#the-low-level-cache-api
use_cache = True


def orm_add_user(user):
    """ Aggiunge un nuovo utente, se non già registrato; restituisce l'istanza dell'utente """

    telegram_user = orm_get_telegram_user(user.id)

    if telegram_user == 0:  # telegram user has not been registered yet
        new_telegram_user = TelegramUser()
        new_telegram_user.user_id = user.id
        new_telegram_user.username = user.username
        new_telegram_user.first_name = user.first_name
        new_telegram_user.last_name = user.last_name
        new_telegram_user.language_code = user.language_code
        new_telegram_user.save()

        # Selezione tutte le categorie (opzione di default)
        for k in Category.objects.all():
            new_telegram_user.categories.add(k)
            k.save()

        new_telegram_user.save()

        print('\nnew telegram user:'
              ' ' + str(new_telegram_user.user_id) +
              ' ' + str(new_telegram_user.username) +
              '  ' + str(new_telegram_user.first_name) + ' ' + str(new_telegram_user.last_name))

        return new_telegram_user

    else:
        print('telegram user: ' + str(telegram_user.user_id))
        return telegram_user


def orm_log_news_sent_to_user(news_item, telegram_user):
    item = NewsItemSentToUser()
    item.telegram_user = telegram_user
    item.news_item = news_item
    item.save()


def orm_add_newsitem(title, text, link):
    """ Aggiunge un nuovo articolo """

    news_id = ''

    # Seleziona un id casule di 5 cifre
    # import random
    # for i in range(5):
    #     news_id += str(random.randint(0, 9))

    # Se l'id è già preso riprova la selezione casuale
    # queryset = NewsItem.objects.filter(news_id=news_id)
    # if len(queryset) != 0:
    #     orm_add_newsitem(title, text, link)

    news = NewsItem()
    # news.news_id = news_id
    news.title = title
    news.text = text
    news.link = link
    news.save()

    print('\nNUOVO ARTICOLO: ' + str(news))

    return news


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
    """ Restituisce l'oggetto user associato a un determinato utente; istanza di tipo TelegramUser """

    def _orm_get_telegram_user():

        queryset_user = TelegramUser.objects.filter(user_id=telegram_user_id)

        if len(queryset_user) == 0:
            result = None
        else:
            result = queryset_user[0]

        return result

    def _orm_get_telegram_user_cache():

        key_name = "user" + telegram_user_id

        result = cache.get(telegram_user_id)

        if result is None:
            result = _orm_get_telegram_user()
            cache.set(telegram_user_id, result, timeout=60)

        return result

    a = datetime.datetime.now()

    if use_cache:
        result = _orm_get_telegram_user_cache()
    else:
        result = _orm_get_telegram_user()

    b = datetime.datetime.now()

    c = b - a

    print("orm_get_telegram_user dt=" + str(c.microseconds) + " microseconds")

    return result


def orm_change_user_privacy_setting(user_id, privacy_setting):
    # print("user_id = " + str(user_id))

    user = orm_get_telegram_user(user_id)

    user.has_accepted_privacy_rules = privacy_setting
    user.privacy_acceptance_mechanism = 'U'

    from django.utils.timezone import now
    user.privacy_acceptance_timestamp = now()

    user.save()


def update_user_category_settings(user, scelta):
    """ Aggiorna le categorie selezionate dall'utente """

    print("update_user_category_settings " + str(scelta))

    queryset_cat = user.categories.filter(key=scelta)

    if len(queryset_cat) != 0:  # La categoria era presente (bisogna rimuoverla)
        cat = queryset_cat[0]
        user.categories.remove(cat)
        user.save()
        cat.save()

        print('RIMOZIONE ' + str(cat))

    else:  # La categoria non era presente (bisogna aggiungerla)
        cat = Category.objects.filter(key=scelta)[0]

        user.categories.add(cat)
        user.save()
        cat.save()

        print('AGGIUNTA ' + str(cat))


# def orm_get_default_categories_dict():
#     """ Restituisce il dizionario contenente le categorie di default """
#     return get_default_categories_dict()


def orm_get_all_telegram_users():
    queryset_user = TelegramUser.objects.all()

    return queryset_user


def orm_get_categories():
    a = datetime.datetime.now()
    queryset = Category.objects.all().order_by('id')
    b = datetime.datetime.now()
    c = b - a
    print("orm_get_categories dt=" + str(c.microseconds) + " microseconds")
    return queryset


def orm_get_last_processed_news():
    news_query = NewsItem.objects.filter(processed=True).order_by('-processed_timestamp')
    # max 5 elements

    # should check if job offer is still active or not
    return news_query


def orm_get_news_to_process():
    news_query = NewsItem.objects.filter(processed=False)

    result = []

    if len(news_query) == 0:
        return result

    now = datetime.datetime.now()

    for news in news_query:

        # to_be_processed = False

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


def orm_get_privacy_rules():
    query_result = SystemParameter.objects.filter(name=UI_PRIVACY)

    if len(query_result) == 0:
        return "***REGOLAMENTO PRIVACY NON DEFINITO***"
    else:
        return query_result[0].value


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

