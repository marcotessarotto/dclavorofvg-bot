from django.core.cache import cache

from tgbot.backoffice.models import NewsItem

use_cache = True


def is_cache_enabled():
    return use_cache


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

