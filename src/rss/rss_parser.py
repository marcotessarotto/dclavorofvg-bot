from src.telegram_bot.ormlayer import *

import feedparser
import os
import django

try:
    from ..backoffice.definitions import RSS_FEED
except:
    from src.backoffice.definitions import RSS_FEED

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_settings")
django.setup()

from src.backoffice.models import SystemParameter, NewsItem, Category


def _orm_get_system_parameter(param_name):
    query_result = SystemParameter.objects.filter(name=param_name)

    if len(query_result) == 0:
        return None
    else:
        return query_result[0].value


def get_feed_entries_from_url(url):

    now = datetime.datetime.now()

    feed = feedparser.parse(url)

    # print (feed)

    for item in feed.entries:

        rss_id = item["id"]
        rss_title = item["title"]
        rss_link = item["link"]
        updated_parsed = item["updated_parsed"]

        d = updated_parsed - datetime.timedelta(days=10)

        if d < now:
            print("too old!")
            continue

        print(item)
        print(rss_title)
        print(item["title_detail"])
        print(rss_link)
        print(rss_id)
        print(updated_parsed)

        # orm_get_or_create_news_from_rss(rss_id, rss_title, rss_link, updated_parsed)



rss_link = _orm_get_system_parameter(RSS_FEED)

if rss_link:
    get_feed_entries_from_url(rss_link)
    pass
