from datetime import datetime, timedelta
from django.utils.timezone import now
from django.core.cache import cache

from src.rss.scraping_utils import get_content_from_regionefvg_news
from src.telegram_bot.log_utils import orm_logger as logger, benchmark_decorator

from src.backoffice.models import *

# https://docs.djangoproject.com/en/2.2/topics/cache/#the-low-level-cache-api
use_cache = True


def _update_user_in_cache(telegram_user):
    if use_cache:
        key_name = "user" + str(telegram_user.user_id)
        cache.set(key_name, telegram_user, timeout=60)


def orm_get_obj_from_cache(obj_name: str):
    """get generic object from django cache"""

    cache_key = "cacheobj" + obj_name

    result = cache.get(cache_key)

    return result


def orm_set_obj_in_cache(obj_name: str, obj_instance, timeout=60*60*12):
    """store object in django cache, default duration is 12 hours"""
    cache_key = "cacheobj" + obj_name

    cache.set(cache_key, obj_instance, timeout=timeout)



def orm_add_telegram_user(user):
    """ creates a new user, if not existing; returns instance of user """

    telegram_user = orm_get_telegram_user(user.id)

    if telegram_user is None:  # telegram user has not been registered yet
        new_telegram_user = TelegramUser()
        new_telegram_user.user_id = user.id
        new_telegram_user.username = user.username
        new_telegram_user.first_name = user.first_name
        new_telegram_user.last_name = user.last_name
        new_telegram_user.language_code = user.language_code
        new_telegram_user.save()

        # new users: should they have all news categories selected? or none?
        if orm_get_system_parameter(CREATE_USER_WITH_ALL_CATEGORIES_SELECTED) == "True":
            # (select all news categories)
            for k in Category.objects.all():
                new_telegram_user.categories.add(k)

        new_telegram_user.save()

        _update_user_in_cache(new_telegram_user)
        logger.info(f"orm_add_telegram_user: new user {new_telegram_user.user_id}")

        return new_telegram_user
    else:
        logger.info(f"orm_add_telegram_user: existing user {telegram_user.user_id}")
        return telegram_user


def orm_log_news_sent_to_user(news_item, telegram_user):
    item = NewsItemSentToUser()
    item.telegram_user = telegram_user
    item.news_item = news_item
    item.save()


def orm_add_news_item(content: str, telegram_user: TelegramUser):
    """create a news item; uses categories from telegram_user"""
    news = NewsItem()

    news.title = f'news da {telegram_user.user_id}'

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
        val = 1
    elif feed == '-':
        news.dislike += 1
        val = -1
    news.save()

    feedback = FeedbackToNewsItem()
    feedback.news = news
    feedback.user = orm_get_telegram_user(telegram_user_id)
    feedback.val = val
    feedback.save()

    logger.debug(f"orm_add_feedback news_id={news_id} telegram_user_id={telegram_user_id} {feed}")


def orm_add_comment(text, news_id, telegram_user_id):
    """ Aggiunge un nuovo commento per l'articolo """

    queryset_user = TelegramUser.objects.filter(user_id=int(telegram_user_id))
    user = queryset_user[0]

    logger.info(f"orm_add_comment id={news_id} user_id={user.id}")

    # https://stackoverflow.com/a/12682379/974287
    Comment.objects.create(user_id=user.id, news_id=news_id, text=text)


def orm_get_comment(user_id):
    """ get all comments posted by a specific user """

    user = TelegramUser.objects.filter(user_id=user_id)[0]
    return Comment.objects.filter(user=user)


@benchmark_decorator
def orm_get_telegram_user(telegram_user_id) -> TelegramUser:
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

        key_name = f"user{telegram_user_id}"

        res = cache.get(key_name)

        if res is None:
            res = _orm_get_telegram_user()
            cache.set(key_name, res, timeout=60)

        return res

    if use_cache:
        result = _orm_get_telegram_user_cache()
    else:
        result = _orm_get_telegram_user()

    # if result is None:
    #     result = orm_add_telegram_user(...)
    #     _update_user_in_cache(result)

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

    logger.info(f"orm_get_user_expected_input({obj}): {res}")

    return res


def orm_has_user_seen_news_item(telegram_user: TelegramUser, news_item: NewsItem) -> bool:

    queryset = NewsItemSentToUser.objects.filter(telegram_user=telegram_user).filter(news_item=news_item)

    return True if len(queryset) > 0 else False


def orm_set_telegram_user_expected_input(obj, expected_input):
    if obj is None:
        return None

    if hasattr(obj, '__dict__'):
        telegram_user = obj
    else:
        telegram_user = orm_get_telegram_user(obj)

    if telegram_user is not None:
        logger.info(
            f"orm_set_user_expected_input: user {telegram_user.user_id}, setting chat_state to {expected_input}")
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
    logger.debug(f"orm_update_telegram_user {telegram_user.user_id}")
    if telegram_user is not None:
        telegram_user.save()
        _update_user_in_cache(telegram_user)


def orm_parse_user_age(telegram_user: TelegramUser, message_text: str):
    """parse age from text sent by user; returns age, -1 for value error"""
    try:
        age = int(message_text)

        if age < 0:
            age = -1
    except ValueError:
        logger.error(f"wrong format for age! {message_text}")
        age = -1

    telegram_user.age = age
    telegram_user.save()
    _update_user_in_cache(telegram_user)
    logger.info(f"parse_user_age: age set for user {telegram_user.user_id} to {age}")

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


def orm_update_user_category_settings(telegram_user, category_key):
    """ Aggiorna le categorie selezionate dall'utente"""

    str_user_id = str(telegram_user.user_id)

    logger.info(f"orm_update_user_category_settings category_key={category_key} user_id={str_user_id}")

    queryset_cat = telegram_user.categories.filter(key=category_key)

    if len(queryset_cat) != 0:  # category is present in user settings, we have to remove it
        cat = queryset_cat[0]
        telegram_user.categories.remove(cat)
        telegram_user.save()

        logger.info(f'orm_update_user_category_settings: remove category={cat.key} user_id={str_user_id}')

    else:  # category is not present in user settings, we have to add it
        cat = Category.objects.filter(key=category_key)[0]

        telegram_user.categories.add(cat)
        telegram_user.save()

        logger.info(f'orm_update_user_category_settings: add category={cat.key} user_id={str_user_id}')


def orm_get_all_telegram_users():
    queryset_user = TelegramUser.objects.all()

    return queryset_user


_skip_list = [UI_HELP_COMMAND, UI_START_COMMAND, UI_HELP_COMMAND_ALT, UI_START_COMMAND_ALT, UI_PRIVACY_COMMAND,
              UI_ME_COMMAND, UI_RESEND_LAST_NEWS_COMMAND, UI_CHOOSE_CATEGORIES_COMMAND,
              UI_FORCE_SEND_NEWS_COMMAND]


def orm_get_categories_valid_command():
    queryset = Category.objects.filter(is_telegram_command=True, custom_telegram_command__isnull=False)\
        .exclude(custom_telegram_command__in=_skip_list)\
        .order_by('key')
    return queryset


@benchmark_decorator
def orm_get_categories():
    queryset = Category.objects.all().order_by('key')
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


@benchmark_decorator
def orm_get_last_processed_news(last_days=10):
    now = datetime.now()

    d = now - timedelta(days=last_days)

    news_query = NewsItem.objects.filter(processed=True).filter(processed_timestamp__gte=d).order_by('-processed_timestamp')

    return news_query


def orm_get_news_item(news_id: int) -> NewsItem:
    news_query = NewsItem.objects.filter(id=news_id)
    return news_query[0] if len(news_query) > 0 else None


def orm_get_fresh_news_to_send():
    news_query = NewsItem.objects.filter(processed=False)

    result = []

    if len(news_query) == 0:
        return result

    now = datetime.now()

    for news in news_query:

        if news.title is None:
            continue

        if news.categories is None:
            continue

        if news.start_publication is not None:
            to_be_processed = news.start_publication <= now
        else:
            to_be_processed = True

        if not to_be_processed:
            continue

        # to be processed!
        result.append(news)

    return result


def orm_get_system_parameter(param_name) -> str:

    def _orm_get_system_parameter(param_name):

        query_result = SystemParameter.objects.filter(name=param_name)

        if len(query_result) == 0:
            return f"*** '{param_name}' parameter is not defined ***"
        else:
            return query_result[0].value

    def _orm_get_system_parameter_cache(param_name):

        key_name = "syspar" + param_name

        result = cache.get(key_name)

        if result is None:
            result = _orm_get_system_parameter(param_name)
            cache.set(key_name, result, timeout=60)

        return result

    if use_cache:
        result = _orm_get_system_parameter_cache(param_name)
    else:
        result = _orm_get_system_parameter(param_name)

    return result


def orm_create_rss_feed_item(rss_id, rss_title, rss_link, updated_parsed):
    queryset = RssFeedItem.objects.filter(rss_id=rss_id)

    if len(queryset) > 0:
        logger.info(f"orm_create_news_from_rss_feed_item: item already processed, rss_id={rss_id}")
        return None

    rss_feed_item = RssFeedItem()
    rss_feed_item.rss_id = rss_id
    rss_feed_item.rss_title = rss_title
    rss_feed_item.rss_link = rss_link
    rss_feed_item.updated_parsed = updated_parsed

    rss_feed_item.save()

    return rss_feed_item


def orm_transform_unprocessed_rss_feed_items_in_news_items():
    """lookup unprocessed rss feed items and generate corresponding news items"""
    queryset = RssFeedItem.objects.filter(processed=False)

    if len(queryset) == 0:
        return None

    for rss_feed_item in queryset:

        # if rss_feed_item.category is None:
        #     continue

        html_content = get_content_from_regionefvg_news(rss_feed_item.rss_link)

        news_item = NewsItem()
        news_item.title_link = rss_feed_item.rss_link
        news_item.title = rss_feed_item.rss_title
        news_item.text = str(html_content)[:2048]  # 2048 is size of html_content field in model RssFeedItem
        news_item.save()

        # news_item.categories.add(rss_feed_item.category)  # news_item needs to have a value for field "id" before this many-to-many relationship can be used.
        # news_item.save()

        rss_feed_item.processed = True
        rss_feed_item.save()

    # send email to admins

    admin_users = TelegramUser.objects.filter(is_admin=True).filter(email__isnull=False)
    for user in admin_users:
        from src.telegram_bot.email_utils import send_email
        send_email(user.email, "bot ", f"RSS feed items transformed into news: {len(queryset)}")


def orm_build_news_stats(last_days=10):
    now = datetime.now()

    d = now - timedelta(days=last_days)

    categories = orm_get_categories()

    result_dict = {}

    for cat in categories:
        # https://docs.djangoproject.com/en/2.2/topics/db/aggregation/
        count = NewsItem.objects.filter(processed=True).filter(processed_timestamp__gte=d).filter(categories__in=[cat]).count()

        result_dict[cat] = count

    return result_dict


def orm_find_ai_action(action: str):
    queryset = AiAction.objects.filter(action=action)

    if len(queryset) == 0:
        return None

    return queryset[0]

