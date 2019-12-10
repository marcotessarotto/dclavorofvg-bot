from functools import wraps

from src.backoffice.definitions import UI_message_accept_privacy_rules_to_continue, UI_message_disabled_account, \
    BOT_LOGS_CHAT_ID
from src.backoffice.models import TelegramUser
from src.telegram_bot.ormlayer import orm_get_telegram_user, orm_add_telegram_user, orm_add_telegram_log_group


def basic_user_checks(update, context):
    telegram_user_id = update.message.chat.id

    if telegram_user_id == BOT_LOGS_CHAT_ID:
        telegram_user = orm_add_telegram_log_group(telegram_user_id)
    else:
        telegram_user = orm_get_telegram_user(telegram_user_id)

    must_return = False

    if check_if_user_is_disabled(telegram_user, update, context):
        must_return = True
    if check_user_privacy_approval(telegram_user, update, context):
        # privacy not yet approved by user
        must_return = True

    return telegram_user_id, telegram_user, must_return


def check_user_privacy_approval(telegram_user: TelegramUser, update, context):
    """return True if user has not yet approved the bot's privacy policy"""

    if telegram_user is None or not telegram_user.has_accepted_privacy_rules:
        print("check_user_privacy_approval - PRIVACY NOT APPROVED  telegram_user_id=" + str(telegram_user.user_id))

        update.message.reply_text(UI_message_accept_privacy_rules_to_continue)
        return True
    else:
        return False


def check_if_user_is_disabled(telegram_user: TelegramUser, update, context):

    if not telegram_user.enabled:
        update.message.reply_text(
            UI_message_disabled_account
        )
        return True
    else:
        return False


def standard_user_checks(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):

        telegram_user_id, telegram_user, must_return = basic_user_checks(update, context)

        if must_return:
            return
        else:
            return func(update, context, telegram_user_id, telegram_user, *args, **kwargs)

    return wrapped

