import os

from src.telegram_bot.log_utils import main_logger as logger, log_user_input, debug_update

from src.telegram_bot.category_utils import _get_category_status, _set_all_categories
from src.telegram_bot.print_utils import my_print

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, KeyboardButton, ReplyKeyboardMarkup, Bot, \
    ChatAction

from src.telegram_bot.news_processing import news_dispatcher, send_news_to_telegram_user, _lookup_file_id_in_message, \
    _get_file_id_for_file_path, intersection, show_news_by_id
from src.telegram_bot.ormlayer import *
from src.telegram_bot.user_utils import basic_user_checks, check_if_user_is_disabled, \
    standard_user_checks

from src.backoffice.definitions import *
from src.backoffice.models import EDUCATIONAL_LEVELS

from telegram.ext import messagequeue as mq, Updater, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler


from src.telegram_bot.regionefvg_bot import *


from pathlib import Path
token_file = Path('token.txt')


def begin_profiling(update, context):
    context.bot.send_message("Inzio raccolta dati")

    # ask age
    ask_age(update, context)
    return CALLBACK_AGE


def ask_age(update, context):
    """ Ask user to enter the age """

    context.bot.send_message(
        chat_id=update.message.chat.id,
        text=UI_message_what_is_your_age,
        parse_mode='HTML',
    )
    return


def callback_age(update, context):

    telegram_user = orm_get_telegram_user(update.message.from_user)
    message_text = update.message.text

    age = orm_parse_user_age(telegram_user, message_text)

    if age >= 80:
        update.message.reply_text(
            UI_message_cheers,
            parse_mode='HTML'
        )

    # now ask educational level
    ask_educational_level(update, context)
    return CALLBACK_EDUCATONAL_LEVEL


def ask_educational_level(update, context):
    """ Ask user to select the educational level in a inline keyboard """

    keyboard = []

    for row in EDUCATIONAL_LEVELS:
        keyboard.append([InlineKeyboardButton(
            text=row[1],
            callback_data=f'education_level {row[0]}')]
        )

    context.bot.send_message(
        chat_id=update.message.chat.id,
        text=UI_message_what_is_your_educational_level,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def callback_education_level(update, context):

    choice = update.callback_query.data

    for line in EDUCATIONAL_LEVELS:
        if line[0] == choice:
            el = line[1]
            break

    telegram_user = orm_get_telegram_user(update.callback_query.from_user.id)

    # logger.info(f"callback_education_level:  {choice}  {el}")

    update.callback_query.edit_message_text(
        text=UI_message_you_have_provided_your_education_level.format(el) +
             UI_message_now_you_can_choose_news_categories
    )

    orm_set_telegram_user_educational_level(telegram_user, choice)

    return


if not token_file.exists():
    token_file = Path('../../token.txt')

token = os.environ.get('TOKEN') or open(token_file).read().strip()

updater = Updater(token=token, use_context=True)
dp = updater.dispatcher


CALLBACK_AGE, CALLBACK_EDUCATONAL_LEVEL = range(2)

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('profil', begin_profiling)],
    states={
        CALLBACK_AGE: [MessageHandler(Filters.text, callback_age)],
        CALLBACK_EDUCATONAL_LEVEL: [CallbackQueryHandler(callback_education_level)]
    },
    fallbacks=[]
)

