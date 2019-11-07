import logging

# https://www.electricmonk.nl/log/2017/08/06/understanding-pythons-logging-module/
from functools import wraps

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

mainlogger = logging.getLogger('regionefvg_bot')  # "main" logger
mainlogger.setLevel(logging.INFO)

ormlogger = logging.getLogger('ormlayer')
ormlogger.setLevel(logging.DEBUG)

newslogger = ormlogger = logging.getLogger('news_processing')
newslogger.setLevel(logging.DEBUG)


#  https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets#advanced-snippets
def log_user_input(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id

        print(f"log_user_input: user_id={user_id}")

        text = update.message.text

        # user_id = update.effective_user.id
        # if user_id not in LIST_OF_ADMINS:
        #     print("Unauthorized access denied for {}.".format(user_id))
        #     return
        return func(update, context, *args, **kwargs)
    return wrapped


