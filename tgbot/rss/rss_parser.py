from tgbot.telegram_bot.ormlayer import *

from datetime import timedelta
from time import mktime
import time

import feedparser
import os
import django

from tgbot.telegram_bot.log_utils import rss_logger as logger

from tgbot.backoffice.definitions import RSS_FEED


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_settings")
django.setup()

from tgbot.backoffice.models import SystemParameter


def _orm_get_system_parameter(param_name):
    query_result = SystemParameter.objects.filter(name=param_name)

    if len(query_result) == 0:
        return None
    else:
        return query_result[0].value


def get_feed_entries_from_url(url):
    import datetime

    dt_now = datetime.datetime.now()
    ten_days_ago = dt_now - timedelta(days=10)

    feed = feedparser.parse(url)
    # print (feed)

    for item in reversed(feed.entries):

        rss_id = item["id"]
        rss_title = item["title"]
        rss_link = item["link"]
        updated_parsed = item["updated_parsed"]
        # print(updated_parsed)

        updated_parsed_dt = datetime.datetime.fromtimestamp(mktime(updated_parsed))

        if updated_parsed_dt < ten_days_ago:
            logger.info(f"rss item too old: {updated_parsed_dt} - {rss_id}")
            continue

        res = orm_create_rss_feed_item(rss_id, rss_title, rss_link, updated_parsed_dt)

        # print(item)
        if res is not None:
            logger.info(f"rss_title: {rss_title}")
            logger.info(f"title_detail: {item['title_detail']}")
            logger.info(f"rss_link: {rss_link}")
            logger.info(f"rss_id: {rss_id}")
            logger.info(f"updated_parsed: {updated_parsed_dt}")
        else:
            logger.info(f"rss item was already processed: {rss_id}")


TIME_TO_SLEEP = 60 * 60  # 1 hour

logger.info("starting rss_parser")

while True:
    rss_feed = _orm_get_system_parameter(RSS_FEED)

    logger.info(f"rss_feed: {rss_feed}")

    if rss_feed:
        get_feed_entries_from_url(rss_feed)

        orm_transform_unprocessed_rss_feed_items_in_news_items()

    logger.info(f"rss_parser, sleeping for {TIME_TO_SLEEP} seconds.")
    time.sleep(TIME_TO_SLEEP)





