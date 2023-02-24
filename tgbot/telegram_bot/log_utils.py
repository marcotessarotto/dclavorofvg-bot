import logging
import time
import datetime
from pytz import timezone as pytz_timezone, utc as pytz_utc

# https://www.electricmonk.nl/log/2017/08/06/understanding-pythons-logging-module/
from functools import wraps

from tgbot.backoffice.definitions import EXT_DEBUG_MSG
from tgbot.telegram_bot.print_utils import my_print

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

print(__file__)


def custom_time_converter(*args):  # https://stackoverflow.com/a/45805464/974287
    utc_dt = pytz_utc.localize(datetime.datetime.utcnow())
    my_tz = pytz_timezone("Europe/Rome")
    converted = utc_dt.astimezone(my_tz)
    return converted.timetuple()


# import time
# logging.Formatter.converter = time.localtime
# logging.Formatter.converter = time.gmtime
logging.Formatter.converter = custom_time_converter

main_logger = logging.getLogger('regionefvg_bot')  # "main" logger
main_logger.setLevel(logging.INFO)

orm_logger = logging.getLogger('ormlayer')
orm_logger.setLevel(logging.DEBUG)

news_logger = logging.getLogger('news_processing')
news_logger.setLevel(logging.DEBUG)

rss_logger = logging.getLogger('rss_parser')
rss_logger.setLevel(logging.DEBUG)

benchmark_logger = logging.getLogger('benchmark')
benchmark_logger.setLevel(logging.DEBUG)

email_logger = logging.getLogger('email')
email_logger.setLevel(logging.DEBUG)

ws_logger = logging.getLogger('ws')
ws_logger.setLevel(logging.INFO)


def benchmark_decorator(func):
    @wraps(func)
    def wrapped(*args, **kwargs):

        # a = datetime.now()
        # https://stackoverflow.com/a/49667269/974287
        # time.time_ns requires python >= 3.7
        a = time.time_ns()

        try:
            return func(*args, **kwargs)
        finally:
            # b = datetime.now()
            b = time.time_ns()

            c = b - a

            if c >= 1000000000:
                benchmark_logger.warning(f"{func.__name__} dt={c / 1000} microseconds")
            else:
                benchmark_logger.debug(f"{func.__name__} dt={c / 1000} microseconds")

    return wrapped


def log_user_input(func):  # https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets#advanced-snippets
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id

        # print(f"log_user_input: user_id={user_id}")
        try:
            text = update.message.text
        except AttributeError:
            text = "?"

        from tgbot.backoffice.models import LogUserInteraction
        cfu = LogUserInteraction()
        cfu.coming_from_user = True
        cfu.text = text
        cfu.user_id = user_id
        cfu.save()

        return func(update, context, *args, **kwargs)
    return wrapped


def debug_update(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        if EXT_DEBUG_MSG:
            main_logger.debug(f"debug_update {func.__name__}:")
            my_print(update, 4, main_logger)
        return func(update, context, *args, **kwargs)
    return wrapped

