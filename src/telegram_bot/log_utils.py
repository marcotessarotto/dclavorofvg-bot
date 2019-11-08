import logging
from datetime import datetime
from pytz import timezone, utc

# https://www.electricmonk.nl/log/2017/08/06/understanding-pythons-logging-module/
from functools import wraps

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def custom_time_converter(*args):  # https://stackoverflow.com/a/45805464/974287

    utc_dt = utc.localize(datetime.utcnow())
    my_tz = timezone("Europe/Rome")
    converted = utc_dt.astimezone(my_tz)
    return converted.timetuple()

# import time
# logging.Formatter.converter = time.localtime
# logging.Formatter.converter = time.gmtime
logging.Formatter.converter = custom_time_converter

mainlogger = logging.getLogger('regionefvg_bot')  # "main" logger
mainlogger.setLevel(logging.INFO)

ormlogger = logging.getLogger('ormlayer')
ormlogger.setLevel(logging.DEBUG)

newslogger = logging.getLogger('news_processing')
newslogger.setLevel(logging.DEBUG)

rsslogger = logging.getLogger('rss_parser')
rsslogger.setLevel(logging.DEBUG)

benchmark_logger = logging.getLogger('benchmark')
benchmark_logger.setLevel(logging.DEBUG)


def benchmark_decorator(func):
    @wraps(func)
    def wrapped(*args, **kwargs):

        a = datetime.now()

        try:
            return func(*args, **kwargs)
        finally:
            b = datetime.now()

            c = b - a

            benchmark_logger.debug(f"benchmark_decorator - {func.__name__} dt={c.microseconds} microseconds")

    return wrapped


def log_user_input(func):  #  https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets#advanced-snippets
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id

        # print(f"log_user_input: user_id={user_id}")

        text = update.message.text

        from src.backoffice.models import CommandsFromUser
        cfu = CommandsFromUser()
        cfu.coming_from_user = True
        cfu.text = text
        cfu.user_id = user_id
        cfu.save()

        return func(update, context, *args, **kwargs)
    return wrapped


