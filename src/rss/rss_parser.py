from src.telegram_bot.ormlayer import *

from datetime import timedelta
from time import mktime

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
    from datetime import datetime

    now = datetime.now()
    ten_days_ago = now - timedelta(days=10)

    feed = feedparser.parse(url)
    # print (feed)

    for item in reversed(feed.entries):

        rss_id = item["id"]
        rss_title = item["title"]
        rss_link = item["link"]
        updated_parsed = item["updated_parsed"]
        # print(updated_parsed)

        updated_parsed_dt = datetime.fromtimestamp(mktime(updated_parsed))

        if updated_parsed_dt < ten_days_ago:
            print("too old!")
            continue

        res = orm_create_news_from_rss_feed_item(rss_id, rss_title, rss_link, updated_parsed_dt)

        # print(item)
        print("rss_title: " + rss_title)
        print("title_detail: " + str(item["title_detail"]))
        print("rss_link: " + rss_link)
        print("rss_id: " + rss_id)
        print("updated_parsed: " + str(updated_parsed_dt))
        print()


rss_link = _orm_get_system_parameter(RSS_FEED)

if rss_link:
    get_feed_entries_from_url(rss_link)
    pass
