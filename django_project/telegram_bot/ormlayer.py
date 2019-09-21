
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_settings")
django.setup()

# Your application specific imports
from django_project.backoffice.models import *


def orm_add_user(user):
    """ Aggiunge un nuovo utente, se non già registrato """

    # {'id': 884401291, 'first_name': 'Marco', 'is_bot': False, 'last_name': 'Tessarotto', 'language_code': 'en'}

    query_result = TelegramUser.objects.filter(user_id=user.id)

    if len(query_result) == 0:  # L'utente user non è ancora registrato
        obj = TelegramUser()
        obj.user_id = user.id
        obj.username = user.username
        obj.first_name = user.first_name
        obj.last_name = user.last_name
        obj.language_code = user.language_code
        obj.save()  # Salva il nuovo utente nella tabella 'telegramuser' dell'applicazione backoffice
        print("TelegramUser added! " + str(obj))

        # Selezione tutte le categorie (opzione di default)
        create_default_keywords_for_user(obj)

        result = obj

    else:   # L'utente user è già stato registrato
        result = query_result[0]

    return result


def orm_add_newsitem(title, text, link):
    """ Aggiunge un nuovo articolo """

    news_id = ''

    import random
    for i in range(5):
        news_id += str(random.randint(0, 9))

    queryset = NewsItem.objects.filter(news_id=news_id)
    if len(queryset) != 0:
        orm_add_newsitem(title, text, link)

    news = NewsItem()
    news.news_id = news_id
    news.title = title
    news.text = text
    news.link = link
    news.save()

    print('\nNUOVO ARTICOLO: ' + str(news))

    return news


def orm_add_feedback(feed, news_id):
    """ Aggiunge un nuovo feedback all'articolo """

    queryset_news = NewsItem.objects.filter(news_id=news_id)
    news = queryset_news[0]

    if feed == '+':
        news.like += 1
    elif feed == '-':
        news.dislike += 1
    news.save()

    print('\nNUOVO FEEDBACK:'
          '\n' + str(news) +
          '\n' + feed)


def orm_add_comment(text, news_id, user_id):
    """ Aggiunge un nuovo commento per l'articolo """

    queryset_news = NewsItem.objects.filter(news_id=news_id)
    news = queryset_news[0]

    queryset_user = TelegramUser.objects.filter(user_id=int(user_id))
    user = queryset_user[0]

    comment = Comment()
    comment.user = user
    comment.news = news
    comment.text = text
    comment.save()

    print('\nNUOVO COMMENTO:'
          '\n' + str(news) +
          '\n' + str(user) +
          '\n\"' + text + '\"')


def orm_get_comment(user_id):
    """ Restituisce i commenti di un determinato utente """

    user = TelegramUser.objects.filter(user_id=user_id)[0]
    return Comment.objects.filter(user=user)


def update_user_category_settings(user, scelta):
    """ Aggiorna le categorie selezionate dall'utente """

    queryset_cat = user.categories.filter(key=scelta)

    if len(queryset_cat) != 0:  # La categoria era presente (bisogna rimuoverla)
        cat = queryset_cat[0]
        user.categories.remove(cat)
        user.save()
        cat.save()

        print('RIMOZIONE ' + str(cat))

    else:   # La categoria non era presente (bisogna aggiungerla)
        cat = Category.objects.filter(key=scelta)[0]

        user.categories.add(cat)
        user.save()
        cat.save()

        print('AGGIUNTA ' + str(cat))


def orm_get_default_categories_dict():
    """ Restituisce il dizionario contenente le categorie di default """

    return get_default_categories_dict()
