import os

from src.telegram_bot.log_utils import main_logger as logger, log_user_input, debug_update

from src.telegram_bot.category_utils import _get_category_status, _set_all_categories

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, KeyboardButton, ReplyKeyboardMarkup, Bot, \
    ChatAction

from src.telegram_bot.news_processing import news_dispatcher, send_news_to_telegram_user, _lookup_file_id_in_message, \
    _get_file_id_for_file_path, intersection, show_news_by_id, send_news_as_audio_file
from src.telegram_bot.ormlayer import *
from src.telegram_bot.solr.solr_client import solr_get_professional_categories

from src.telegram_bot.user_utils import basic_user_checks, check_if_user_is_disabled, \
    standard_user_checks

from src.backoffice.definitions import *
from src.backoffice.models import EDUCATIONAL_LEVELS

from telegram.ext import messagequeue as mq, Updater, ConversationHandler, CommandHandler, MessageHandler, Filters, \
    CallbackQueryHandler, run_async

from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)

import time

# set in main method
global_bot_instance = None

CALLBACK_PRIVACY, CALLBACK_AGE, CALLBACK_EDUCATIONAL_LEVEL, CALLBACK_CUSTOM_EDUCATIONAL_LEVEL = range(4)


def send_message_to_log_group(text):
    """send bot log message to dedicated chat"""
    if not text or not global_bot_instance:
        return

    try:

        global_bot_instance.send_message(
            chat_id=BOT_LOGS_CHAT_ID,
            text=text,
        )
    except Exception:
        logger.error("send_message_to_log_group")


@debug_update
@log_user_input
def start_command_handler(update, context):
    logger.info(f"start args: {context.args}")  # parameter received through start command; max length: 64
    # example:
    # https://telegram.me/DCLavoroFvg_bot?start=12345

    # logger.info("update.message.from_user = " + str(update.message.from_user))

    telegram_user = orm_add_telegram_user(update.message.from_user)

    if check_if_user_is_disabled(telegram_user, update, context):
        return ConversationHandler.END

    bot_presentation = orm_get_system_parameter(UI_bot_presentation)

    update.message.reply_text(
        f'{UI_HELLO} {update.message.from_user.first_name}! {bot_presentation}'
    )

    # if check_user_privacy_approval(telegram_user, update, context):
    if not telegram_user.has_accepted_privacy_rules:
        # privacy not yet approved by user
        return privacy_command_handler(update, context)

    return ConversationHandler.END


def privacy_command_handler(update, context):
    """ Ask user to accept privacy rules, if they were not yet accepted """

    telegram_user = orm_get_telegram_user(update.message.from_user.id)
    privacy_state = telegram_user.has_accepted_privacy_rules

    logger.info(f"privacy_command_handler - user id={telegram_user.id} privacy accepted: {privacy_state}")

    if not privacy_state:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=UI_message_read_and_accept_privacy_rules_as_follows + orm_get_system_parameter(UI_PRIVACY),
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[UI_ACCEPT_UC, UI_NOT_ACCEPT_UC]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
        )

        return CALLBACK_PRIVACY

    # https://stackoverflow.com/a/17311079/974287
    update.message.reply_text(
        text=UI_message_you_have_accepted_privacy_rules_on_this_day +
             telegram_user.privacy_acceptance_timestamp.strftime(DATE_FORMAT_STR) + '\n' +
             orm_get_system_parameter(UI_PRIVACY),
        parse_mode='HTML'
    )

    return ConversationHandler.END


def callback_privacy(update, context):
    choice = update.message.text

    if choice == UI_ACCEPT_UC:
        privacy_setting = True
    elif choice == UI_NOT_ACCEPT_UC:
        privacy_setting = False
    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=UI_message_error_accepting_privacy_rules.format(UI_ACCEPT_UC, UI_NOT_ACCEPT_UC),
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[UI_ACCEPT_UC, UI_NOT_ACCEPT_UC]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
        )
        return CALLBACK_PRIVACY

    telegram_user_id = update.message.from_user.id
    orm_change_user_privacy_setting(telegram_user_id, privacy_setting)

    if privacy_setting:
        update.message.reply_text(UI_message_thank_you_for_accepting_privacy_rules)

        ask_age(update, context)
        return CALLBACK_AGE
    else:
        update.message.reply_text(UI_message_you_have_not_accepted_privacy_rules_cannot_continue)
        return ConversationHandler.END


def ask_age(update, context):
    """ Ask user to enter the age """

    update.message.reply_text(UI_message_what_is_your_age)
    return


def callback_age(update, context):
    telegram_user = orm_get_telegram_user(update.message.from_user.id)
    age = update.message.text

    age = orm_parse_user_age(telegram_user, age)
    if age >= 80:
        reply_text = UI_message_cheers
    else:
        reply_text = UI_message_you_have_provided_your_age

    update.message.reply_text(reply_text)

    # now ask educational level
    ask_educational_level(update, context)
    return CALLBACK_EDUCATIONAL_LEVEL


def ask_educational_level(update, context):
    """ Ask user to select the educational level """

    keyboard = []

    k_row = []
    for row in EDUCATIONAL_LEVELS:
        if len(k_row) == 2:
            keyboard.append(k_row)
            k_row = []
        k_row.append(row[1])
    if len(k_row) > 0:
        keyboard.append(k_row)

    # print(keyboard)

    context.bot.send_message(
        chat_id=update.message.chat.id,
        text=UI_message_what_is_your_educational_level,
        parse_mode='HTML',
        reply_markup=ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )


def callback_education_level(update, context):
    choice = update.message.text

    if choice == EDUCATIONAL_LEVELS[-1][1]:
        update.message.reply_text(UI_message_enter_custom_educational_level)
        return CALLBACK_CUSTOM_EDUCATIONAL_LEVEL

    for line in EDUCATIONAL_LEVELS:
        if line[1] == choice:
            el = line[0]
            break

    telegram_user = orm_get_telegram_user(update.message.from_user.id)

    logger.info(f"callback_education_level:  {choice} {el}")

    update.message.reply_text(
        text=UI_message_you_have_provided_your_education_level.format(choice),
        parse_mode='HTML'
    )
    update.message.reply_text(UI_message_now_you_can_choose_news_categories)

    orm_set_telegram_user_educational_level(telegram_user, el)
    return ConversationHandler.END


def callback_custom_education_level(update, context):
    """ Read the custom education level """

    choice = EDUCATIONAL_LEVELS[-1][0]
    el = EDUCATIONAL_LEVELS[-1][1]
    telegram_user = orm_get_telegram_user(update.message.from_user.id)

    # Change the models.py and the admin.py modules to register a custom educational level
    custom_education_level = update.message.text

    logger.info(f"callback_education_level:  {choice}")

    update.message.reply_text(UI_message_you_have_provided_your_education_level.format(custom_education_level))
    update.message.reply_text(UI_message_now_you_can_choose_news_categories)

    orm_set_telegram_user_educational_level(telegram_user, choice)
    return ConversationHandler.END


def fallback_conversation_handler(update, context):
    text = update.message.text
    logger.info(f'fallback_conversation_handler {text}')
    return ConversationHandler.END


def undo_privacy_command_handler(update, context):
    orm_change_user_privacy_setting(update.message.from_user.id, False)

    logger.info(f"undo_privacy_command_handler - telegram user id={update.message.from_user.id}")

    update.message.reply_text(
        UI_message_your_privacy_acceptance_has_been_deleted,
        parse_mode='HTML'
    )


@benchmark_decorator
def help_command_handler(update, context):
    """ Show available bot commands"""

    update.message.reply_text(
        orm_get_system_parameter(UI_bot_help_message),
        parse_mode='HTML'
    )


@benchmark_decorator
def help_categories_command_handler(update, context):
    categories = orm_get_categories_valid_command()
    msg = UI_message_categories_selection
    for cat in categories:
        msg = msg + f'<b>/{cat.custom_telegram_command}</b> {UI_arrow} categoria "{cat.name}"\n'

    update.message.reply_text(
        msg,
        parse_mode='HTML'
    )


# @run_async
@benchmark_decorator
def callback(update, context):
    """process callback data sent by inline_keyboards """

    data = update.callback_query.data.split()
    # I dati inviati dalle callback_query sono organizzati come segue:
    # il primo elemento contiente una stringa identificativa del contesto
    # il secondo elemento (e eventuali successivi) contiene i dati da passare

    keyword = data[0]

    logger.info(f"callback {keyword}")

    if keyword == 'feedback':  # Callback per i feedback agli articoli
        callback_feedback(update, data[1:])

    elif keyword == 'comment':  # Callback per i commenti agli articoli
        callback_comment(update, context, data[1])

    elif keyword == 'choice':  # Callback per la scelta delle categorie
        callback_choice(update, data[1])


@log_user_input
@standard_user_checks
@run_async
@benchmark_decorator
def show_news_command_handler(update, context, telegram_user_id, telegram_user):
    """show a specific news item (identified by id)"""

    str_id = update.message.text.replace('/' + UI_SHOW_NEWS, '')
    if str_id is '':
        return

    news_id = int(str_id)

    logger.info(f"show_news_command_handler: {str_id}")

    if show_news_by_id(context, news_id, telegram_user):
        return

    # update.message.reply_text(id, parse_mode='Markdown')


@log_user_input
@standard_user_checks
@run_async
@benchmark_decorator
def read_news_item_command_handler(update, context, telegram_user_id, telegram_user):
    """read a specific news item (identified by id)"""

    str_id = update.message.text.replace('/' + UI_READ_NEWS, '')
    if str_id is '':
        return

    news_id = int(str_id)

    logger.info(f"read_news_item_command_handler: {str_id}")

    send_news_as_audio_file(context, news_id, telegram_user)


@log_user_input
@standard_user_checks
def choose_news_categories_command_handler(update, context, telegram_user_id, telegram_user):
    """let user choose news categories to which subscribe"""
    # telegram_user_id, telegram_user, must_return = basic_user_checks(update, context)
    # if must_return:
    #     return

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=UI_message_select_news_categories,
        reply_markup=InlineKeyboardMarkup(inline_keyboard(telegram_user))
    )


def inline_keyboard(user):
    """ Costruisce la inline_keyboard in base alle categorie già scelte
    dall'utente passato per parametro """

    keyboard = []

    all_categories = orm_get_categories()

    user_categories_set = set(user.categories.all())

    for cat in all_categories:

        if cat.emoji is not None:
            label = cat.name + ' ' + cat.emoji
        else:
            label = cat.name

        if cat in user_categories_set:
            label = u'\U00002705' + ' ' + label.upper()
        else:
            label = u'\U0000274C' + ' ' + label

        keyboard.append([InlineKeyboardButton(
            text=label,
            callback_data='choice ' + cat.key)]
        )

    # add close button
    keyboard.append(
        [InlineKeyboardButton(text=UI_CLOSE_UC, callback_data='choice OK')]
    )

    return keyboard


@benchmark_decorator
def callback_choice(update, choice: str):
    telegram_user = orm_get_telegram_user(update.callback_query.from_user.id)

    if choice == 'OK':  # show choosen categories
        choosen_categories = telegram_user.categories_str()

        # no category has been choosen
        if choosen_categories == '':
            update.callback_query.edit_message_text(
                text=UI_message_you_have_choosen_no_categories +
                     UI_message_you_can_modify_categories_with_command
            )
        else:
            update.callback_query.edit_message_text(
                text=UI_message_you_have_choosen_the_following_categories +
                     choosen_categories +
                     UI_message_you_can_modify_categories_with_command
            )

    else:  # Toggle checked/unchecked per la categoria selezionata
        orm_update_user_category_settings(telegram_user, choice)

        update.callback_query.edit_message_text(
            text=UI_message_select_news_categories,
            reply_markup=InlineKeyboardMarkup(inline_keyboard(telegram_user))
        )


@log_user_input
@standard_user_checks
def custom_command_handler(update, context, telegram_user_id, telegram_user):
    original_command = update.message.text

    logger.info(f"custom_command_handler: {original_command}")

    custom_telegram_command = original_command[1:]

    categories = orm_get_categories_valid_command()

    cat = next((cat for cat in categories if cat.custom_telegram_command == custom_telegram_command), None)

    # if custom_telegram_command not in [cat.custom_telegram_command for cat in categories]:
    if cat is None:
        update.message.reply_text(
            UI_message_no_matching_category_command,
            parse_mode='HTML'
        )
        return

    status = _get_category_status(update, context, custom_telegram_command)

    msg = (
        UI_message_you_are_subscribed_to_news_category if status else UI_message_you_are_not_subscribed_to_news_category).format(
        cat.name)

    if status:
        msg = msg + UI_message_continue_sending_news_about.format(cat.name)
    else:
        msg = msg + UI_message_do_you_want_news_about.format(cat.name)

    custom_command_ok_keyboard = KeyboardButton(text=cat.name + UI_message_ok_suffix)
    custom_command_no_keyboard = KeyboardButton(text=cat.name + UI_message_no_suffix)

    custom_keyboard = [[custom_command_ok_keyboard, custom_command_no_keyboard]]

    reply_markup = ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True, one_time_keyboard=True)

    update.message.reply_text(
        msg,
        parse_mode='HTML',
        reply_markup=reply_markup
    )


@log_user_input
@standard_user_checks
def set_all_categories_command_handler(update, context, telegram_user_id, telegram_user):
    _set_all_categories(update, context, True)


@log_user_input
@standard_user_checks
def set_no_categories_command_handler(update, context, telegram_user_id, telegram_user):
    _set_all_categories(update, context, False)


# to be changed or removed
def me_command_handler(update, context):
    telegram_user_id, telegram_user, must_return = basic_user_checks(update, context)
    if must_return:
        return

    # update.message.reply_text(
    #     UI_message_help_me_provide_better_results,
    #     parse_mode='HTML',
    #     # reply_markup=reply_markup
    # )

    # update.message.reply_text(
    #     UI_message_do_you_need_examples_on_me_command,
    #     parse_mode='HTML',
    #     # reply_markup=reply_markup
    # )

    me_continue_keyboard = KeyboardButton(text=UI_message_let_me_ask_you_some_questions)
    me_stop_keyboard = KeyboardButton(text=UI_message_me_stop_questions)

    custom_keyboard = [[me_continue_keyboard, me_stop_keyboard]]

    reply_markup = ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True, one_time_keyboard=True)

    update.message.reply_text(
        UI_message_help_me_provide_better_results,
        parse_mode='HTML',
        reply_markup=reply_markup
    )


@log_user_input
@standard_user_checks
@run_async
@benchmark_decorator
def resend_last_processed_news_command_handler(update, context, telegram_user_id, telegram_user):
    logger.info("resend_last_processed_news")

    now = datetime.now()

    lrn = context.user_data.get('last_resend_news_timestamp')

    # if telegram_user.resend_news_timestamp is not None and telegram_user.resend_news_timestamp > now - timedelta(minutes=1):
    if lrn is not None and lrn > now - timedelta(minutes=1):
        logger.warning("resend_last_processed_news_command_handler: too frequent! skipping")
        context.bot.send_message(
            chat_id=telegram_user.user_id,
            text=UI_message_already_resent_news,
            parse_mode='HTML'
        )
        return

    # telegram_user.resend_news_timestamp = now
    # orm_update_telegram_user(telegram_user)

    context.user_data['last_resend_news_timestamp'] = now

    news_query = orm_get_last_processed_news()

    logger.info(f"resend_last_processed_news - processed news items={len(news_query)}")

    if len(news_query) == 0:
        context.bot.send_message(
            chat_id=telegram_user.user_id,
            text=UI_message_no_previous_news_to_send_again,
            parse_mode='HTML'
        )
        return

    telegram_user_categories = telegram_user.categories.all()

    counter = 0

    for news_item in reversed(news_query[:MAX_NUM_NEWS_TO_RESEND]):

        intersection_result = intersection(news_item.categories.all(), telegram_user_categories)

        if news_item.broadcast_message is not True and len(intersection_result) == 0:
            continue

        logger.info(
            f"resend_last_processed_news - resending news_item.id={news_item.id} to user {telegram_user.user_id}")

        news_item_already_shown_to_user = orm_has_user_seen_news_item(telegram_user, news_item)

        send_news_to_telegram_user(context, news_item, telegram_user, intersection_result=intersection_result,
                                   request_feedback=False, title_only=True,
                                   news_item_already_shown_to_user=news_item_already_shown_to_user)

        counter += 1

        time.sleep(200 / 1000)

    if counter == 0:
        context.bot.send_message(
            chat_id=telegram_user.user_id,
            text=UI_message_no_matching_previous_news,
            parse_mode='HTML'
        )


@log_user_input
@standard_user_checks
def force_send_news_command_handler(update, context, telegram_user_id, telegram_user):
    if not telegram_user.is_admin:
        return

    context.bot.send_message(
        chat_id=telegram_user.user_id,
        text="ok admin, starting news dispatcher...",
        parse_mode='HTML'
    )

    logger.info("force_send_news_command_handler")
    news_dispatcher(context)


@log_user_input
@standard_user_checks
def stats_command_handler(update, context, telegram_user_id, telegram_user):
    dict = orm_build_news_stats()
    # logger.info(dict)

    text = UI_statistics_on_news

    for k, v in dict.items():
        # logger.info("k=" + str(k) + " v=" + str(v))
        text += str(k.name) + ': ' + str(v) + "\n"

    context.bot.send_message(
        chat_id=telegram_user.user_id,
        text=text,
        parse_mode='HTML'
    )


@log_user_input
@standard_user_checks
def audio_on_command_handler(update, context, telegram_user_id, telegram_user: TelegramUser):
    telegram_user.is_text_to_speech_enabled = True

    orm_update_telegram_user(telegram_user)

    context.bot.send_message(
        chat_id=telegram_user.user_id,
        text=UI_message_text_to_speech_has_been_enabled,
        parse_mode='HTML'
    )


@log_user_input
@standard_user_checks
def audio_off_command_handler(update, context, telegram_user_id, telegram_user):
    telegram_user.is_text_to_speech_enabled = False

    orm_update_telegram_user(telegram_user)

    context.bot.send_message(
        chat_id=telegram_user.user_id,
        text=UI_message_text_to_speech_has_been_disabled,
        parse_mode='HTML'
    )


@log_user_input
@standard_user_checks
def show_professional_categories_command_handler(update, context, telegram_user_id, telegram_user):

    dict = solr_get_professional_categories()

    text = UI_message_professional_categories_stats

    for k, v in dict.items():
        text += f"{k} {UI_arrow} {v}\n"

    context.bot.send_message(
        chat_id=telegram_user.user_id,
        text=text,
        parse_mode='HTML'
    )


@log_user_input
@standard_user_checks
def debug2_command_handler(update, context, telegram_user_id, telegram_user):
    if not telegram_user.is_admin:
        return

    logger.info("debug2_command_handler")

    orm_change_user_privacy_setting(telegram_user_id, False)

    context.bot.send_message(
        chat_id=telegram_user.user_id,
        text='ok admin, just reset your privacy settings',
        parse_mode='HTML'
    )

    pass


@log_user_input
@standard_user_checks
def debug3_command_handler(update, context, telegram_user_id, telegram_user):
    if not telegram_user.is_admin:
        return

    fp = '/opt/media/dclavorofvg-bot/uploads/2019/10/23/external-content.duckduckgo.com.jpeg'

    file_id = _get_file_id_for_file_path(fp)

    logger.info(f"debug3_command_handler: file_id found? {file_id}")

    m = context.bot.send_photo(telegram_user_id, file_id if file_id is not None else open(fp, 'rb'))

    _lookup_file_id_in_message(m, fp, file_id)


@log_user_input
@standard_user_checks
def debug4_command_handler(update, context, telegram_user_id, telegram_user):
    if not telegram_user.is_admin:
        return

    from time import sleep

    logger.info("sleep 0 ms")
    for i in range(100):
        orm_get_telegram_user(telegram_user_id)
        # sleep(0.10)

    logger.info("sleep 50 ms")
    for i in range(100):
        orm_get_telegram_user(telegram_user_id)
        sleep(0.05)

    logger.info("sleep 100 ms")
    for i in range(100):
        orm_get_telegram_user(telegram_user_id)
        sleep(0.10)


@log_user_input
@standard_user_checks
@run_async
def ping_command_handler(update, context, telegram_user_id, telegram_user):
    """get status of system services - admin command"""
    if not telegram_user.is_admin:
        return

    system_services = ['gunicorn', 'rssparser', 'postgresql']

    import subprocess

    text = 'system services status:\n'

    for service_name in system_services:
        a = subprocess.run(["systemctl", "status", "--output=json", service_name])

        text += f"{service_name}: {a.returncode}\n"

    # how many users
    text += f"users: {len(TelegramUser.objects.all())}\n"

    context.bot.send_message(
        chat_id=telegram_user.user_id,
        text=text,
        parse_mode='HTML'
    )


@log_user_input
@standard_user_checks
def cleanup_command_handler(update, context, telegram_user_id, telegram_user):
    """delete all NewsItemSentToUser instances - admin command"""
    if not telegram_user.is_admin:
        return

    logger.info("cleanup_command_handler")

    NewsItemSentToUser.objects.all().delete()

    pass


@log_user_input
@standard_user_checks
@run_async
def admin_send_command_handler(update, context, telegram_user_id, telegram_user):
    """create a news item - admin command"""
    # takes content after /news command as content of the news to send

    # admin only
    if not telegram_user.is_admin:
        return

    data = update.message.text[len(UI_SEND_NEWS_COMMAND) + 1:].strip()

    words = data.split()

    s = words[0]

    if (s.startswith('-') and s[1:].isdigit()) or s.isdigit():
        chat_id = s
        data = " ".join(words[1:])

        context.bot.send_message(
            chat_id=chat_id,
            text=data,
        )

        return

    logger.info(f"sendnews_command_handler: {data}")

    orm_add_news_item(data, telegram_user)


def callback_feedback(update, data):
    """manage feedback about news items """

    feed = data[0]
    news_id = data[1]
    comment_enabled = data[2]

    if comment_enabled == "True":
        comment_enabled = True
    elif comment_enabled == "False":
        comment_enabled = False
    else:
        logger.info(f"wrong value for comment_enabled: {comment_enabled}")

    logger.info(f"callback_feedback feed={feed} news_id={news_id} comment_enabled={comment_enabled}")
    orm_add_feedback(feed, news_id, update.callback_query.message.chat.id)

    if comment_enabled:
        # show keyboard with 'commenta' button
        update.callback_query.edit_message_text(
            text=UI_message_thank_you_for_feedback_newline + UI_message_write_a_comment,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    text=UI_message_write_a_comment_button,
                    callback_data=f'comment {news_id}')]
            ])
        )
    else:
        update.callback_query.edit_message_text(
            text=UI_message_thank_you_for_feedback,
        )


def callback_comment(update, context, news_id):
    """send a comment about an article"""
    logger.info("callback_comment")

    # remove button 'commenta'
    update.callback_query.edit_message_text(
        UI_message_thank_you_for_feedback
    )

    # send a message which will become a reply containing a comment to  news item
    context.bot.send_message(
        chat_id=update.callback_query.message.chat_id,
        text=UI_message_comment_to_news_item + str(news_id),
        reply_markup=ForceReply()  # Invite user to respond to this message (and thus provide a comment)
    )


def comment_handler(update, context):
    """ save the comment provided by user """

    logger.info(f"comment_handler: reply_to_message.text message={update.message.reply_to_message.text}")
    logger.info(f"comment_handler: message.text message={update.message.text}")

    if not update.message.reply_to_message.text.startswith(UI_message_comment_to_news_item):
        logger.info("comment_handler - not a comment for a news item")
        return

    reply_data = update.message.reply_to_message.text.split()
    # logger.info(reply_data)
    orm_add_comment(update.message.text, reply_data[3], update.message.chat.id)

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=UI_message_comment_successful
    )


@log_user_input
@standard_user_checks
def generic_message_handler(update, context, telegram_user_id, telegram_user):

    message_text = update.message.text

    logger.info(f"generic_message_handler - message_text = {message_text}")

    expected_input = orm_get_user_expected_input(telegram_user)

    if expected_input == 'a':  # expecting age from user
        callback_age(update, context, telegram_user, message_text)
        return

    if message_text.lower() in help_keyword_list or len(message_text) <= 2:
        update.message.reply_text(
            orm_get_system_parameter(UI_bot_help_message),
            parse_mode='HTML'
        )
    else:
        global_bot_instance.send_chat_action(chat_id=telegram_user_id, action=ChatAction.TYPING)
        # generic user utterance
        orm_store_free_text(message_text, telegram_user)


# def callback_minute(context: telegram.ext.CallbackContext):
#     all_telegram_users = orm_get_all_telegram_users()
#
#     for telegram_user in all_telegram_users:
#         print("*** " + str(telegram_user.user_id))
#
#         context.bot.send_message(chat_id=telegram_user.user_id,
#                                  text='One message every 10 minutes')


class MQBot(Bot):
    """A subclass of Bot which delegates send method handling to MQ"""

    def __init__(self, *args, is_queued_def=True, mqueue=None, **kwargs):
        super(MQBot, self).__init__(*args, **kwargs)
        # below 2 attributes should be provided for decorator usage
        self._is_messages_queued_default = is_queued_def
        self._msg_queue = mqueue or mq.MessageQueue()

    def __del__(self):
        try:
            self._msg_queue.stop()
        except:
            pass

    @mq.queuedmessage
    def send_message(self, *args, **kwargs):
        '''Wrapped method would accept new `queued` and `isgroup`
        OPTIONAL arguments'''
        return super(MQBot, self).send_message(*args, **kwargs)


def error_callback(update, error):
    logger.error("***error_callback***")
    logger.error(update)
    logger.error(error)

    try:
        raise error
    except Unauthorized:
        # remove update.message.chat_id from conversation list
        # logger.error(error)
        logger.error("Unauthorized")
    except BadRequest:
        # handle malformed requests - read more below!
        # logger.error(error)
        logger.error("BadRequest")
    except TimedOut:
        # handle slow connection problems
        # logger.error(error)
        logger.error("TimedOut")
    except NetworkError:
        # handle other connection problems
        # logger.error(error)
        logger.error("NetworkError")
    except ChatMigrated as e:
        # the chat_id of a group has changed, use e.new_chat_id instead
        # print(error)
        logger.error("ChatMigrated")
    except TelegramError:
        # handle all other telegram related errors
        # print(error)
        logger.error("TelegramError")

    now = datetime.datetime.now()

    send_message_to_log_group(f"{now}\n{update}\n{error}")


def main():
    logger.info("starting bot...")

    from telegram.utils.request import Request

    from pathlib import Path
    token_file = Path('token.txt')

    if not token_file.exists():
        token_file = Path('../../token.txt')

    token = os.environ.get('TOKEN') or open(token_file).read().strip()

    # https://github.com/python-telegram-bot/python-telegram-bot/wiki/Avoiding-flood-limits
    q = mq.MessageQueue(all_burst_limit=29, all_time_limit_ms=1017)  # 5% safety margin in messaging flood limits
    # set connection pool size for bot
    request = Request(con_pool_size=8)
    my_bot = MQBot(token, request=request, mqueue=q)

    global global_bot_instance
    global_bot_instance = my_bot

    updater = Updater(bot=my_bot, use_context=True)
    dp = updater.dispatcher

    job_queue = updater.job_queue

    logger.info(f"news check period: {NEWS_CHECK_PERIOD} s")
    job_minute = job_queue.run_repeating(news_dispatcher, interval=NEWS_CHECK_PERIOD, first=0)  # callback_minute

    # Handler to start user iteration
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler(UI_PRIVACY_COMMAND, privacy_command_handler),
            CommandHandler(UI_START_COMMAND, start_command_handler),
            CommandHandler(UI_START_COMMAND_ALT, start_command_handler)
        ],
        states={
            CALLBACK_PRIVACY: [MessageHandler(Filters.text, callback_privacy)],
            CALLBACK_AGE: [MessageHandler(Filters.text, callback_age)],
            CALLBACK_EDUCATIONAL_LEVEL: [MessageHandler(Filters.text, callback_education_level)],
            CALLBACK_CUSTOM_EDUCATIONAL_LEVEL: [MessageHandler(Filters.text, callback_custom_education_level)]
        },
        fallbacks=[
            MessageHandler(Filters.all, fallback_conversation_handler)
        ]
    )
    dp.add_handler(conv_handler)

    # Handler to serve categories, feedbacks and comments inline keboards
    dp.add_handler(CallbackQueryHandler(callback))

    # Other handlers
    dp.add_handler(CommandHandler(UI_HELP_COMMAND, help_command_handler))
    if UI_HELP_COMMAND_ALT is not None:
        dp.add_handler(CommandHandler(UI_HELP_COMMAND_ALT, help_command_handler))

    dp.add_handler(CommandHandler(UI_UNDO_PRIVACY_COMMAND, undo_privacy_command_handler))

    # These are 'standard' commands (add all categories / remove all categories)
    dp.add_handler(CommandHandler(UI_ALL_CATEGORIES_COMMAND, set_all_categories_command_handler))
    dp.add_handler(CommandHandler(UI_NO_CATEGORIES_COMMAND, set_no_categories_command_handler))

    dp.add_handler(CommandHandler(UI_ME_COMMAND, me_command_handler))

    dp.add_handler(CommandHandler(UI_RESEND_LAST_NEWS_COMMAND, resend_last_processed_news_command_handler))
    dp.add_handler(MessageHandler(Filters.reply, comment_handler))
    dp.add_handler(MessageHandler(Filters.text, generic_message_handler))

    dp.add_handler(CommandHandler(UI_CHOOSE_CATEGORIES_COMMAND, choose_news_categories_command_handler))
    # dp.add_handler(CommandHandler(UI_SHOW_NEWS, show_news_command_handler))
    dp.add_handler(MessageHandler(Filters.regex('^(/' + UI_SHOW_NEWS + '[\\d]+)$'), show_news_command_handler))
    dp.add_handler(MessageHandler(Filters.regex('^(/' + UI_READ_NEWS + '[\\d]+)$'), read_news_item_command_handler))

    dp.add_handler(CommandHandler(UI_CATEGORIES_HELP, help_categories_command_handler))

    dp.add_handler(CommandHandler(UI_FORCE_SEND_NEWS_COMMAND, force_send_news_command_handler))
    dp.add_handler(CommandHandler(UI_DEBUG2_COMMAND, debug2_command_handler))
    dp.add_handler(CommandHandler(UI_DEBUG3_COMMAND, debug3_command_handler))
    dp.add_handler(CommandHandler(UI_DEBUG4_COMMAND, debug4_command_handler))

    dp.add_handler(CommandHandler(UI_PING_COMMAND, ping_command_handler))
    dp.add_handler(CommandHandler(UI_SEND_NEWS_COMMAND, admin_send_command_handler))
    dp.add_handler(CommandHandler(UI_CLEANUP_COMMAND, cleanup_command_handler))

    dp.add_handler(CommandHandler(UI_STATS_COMMAND, stats_command_handler))

    dp.add_handler(CommandHandler(UI_AUDIO_ON_COMMAND, audio_on_command_handler))
    dp.add_handler(CommandHandler(UI_AUDIO_OFF_COMMAND, audio_off_command_handler))

    dp.add_handler(CommandHandler(UI_SHOW_PROFESSIONAL_CATEGORIES_COMMAND, show_professional_categories_command_handler))

    # catch all unknown commands (including custom commands associated to categories)
    dp.add_handler(MessageHandler(Filters.command, custom_command_handler))

    # https://github.com/python-telegram-bot/python-telegram-bot/wiki/Exception-Handling
    dp.add_error_handler(error_callback)

    # start updater
    updater.start_polling()

    # Stop the bot if you have pressed Ctrl + C or the process has received SIGINT, SIGTERM or SIGABRT
    updater.idle()

    logger.info("terminating bot")


if __name__ == '__main__':
    main()
