
# cd Scrivania/regionefvg_bot
# export PYTHONPATH=.:src/telegram_bot
# python src/telegram_bot/regionefvg_bot.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, KeyboardButton, ReplyKeyboardMarkup, Bot, \
    ChatAction

from src.telegram_bot.ormlayer import *

try:
    from ..backoffice.definitions import *
    from ..backoffice.models import EDUCATIONAL_LEVELS
except:
    from src.backoffice.definitions import *
    from src.backoffice.models import EDUCATIONAL_LEVELS

# from telegram.ext import *

from telegram.ext import messagequeue as mq, Updater, CommandHandler, MessageHandler, Filters, CallbackContext, \
    CallbackQueryHandler

import logging

from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)

from src.gfvgbo.settings import MEDIA_ROOT

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

global_bot_instance = None


def check_user_privacy_approval(telegram_user: TelegramUser, update, context):
    """return True if user has not yet approved the bot's privacy policy"""

    if telegram_user is None or not telegram_user.has_accepted_privacy_rules:
        print("check_user_privacy_approval - PRIVACY NOT APPROVED  telegram_user_id=" + str(telegram_user.user_id))

        update.message.reply_text(UI_message_accept_privacy_rules_to_continue)
        return True
    else:
        return False


def check_user_is_enabled(telegram_user: TelegramUser, update, context):
    if not telegram_user.enabled:
        update.message.reply_text(
            UI_message_disabled_account
        )
        return True
    else:
        return False


def my_print(obj, indent):
    mydic = obj.__dict__
    for i in mydic:
        name = str(i)
        val = mydic[i]
        if val is not None:

            if name == "message" or name == "callback_query":
                print(" " * indent + name + " : ")
                my_print(val, indent + 4)
            else:
                print(" " * indent + name + " : " + str(val))
        else:
            # print(" " * indent + name + " : None")
            pass


def start_command_handler(update, context):

    if DEBUG_MSG:
        print("start_command_handler update:")
        my_print(update, 4)

    print("start args:" + str(context.args))  # parametro via start; max 64 caratteri
    # https://telegram.me/marcotts_bot?start=12345

    # print("update.message.from_user = " + str(update.message.from_user))

    telegram_user = orm_add_telegram_user(update.message.from_user)

    if check_user_is_enabled(telegram_user, update, context):
        return

    bot_presentation = orm_get_system_parameter(UI_bot_presentation)

    update.message.reply_text(
        'Ciao ' + update.message.from_user.first_name + '! ' + bot_presentation
    )

    # if check_user_privacy_approval(telegram_user, update, context):
    if not telegram_user.has_accepted_privacy_rules:
        # privacy not yet approved by user
        return privacy_command_handler(update, context)

    # update.message.reply_text(
    #     orm_get_system_parameter(UI_bot_help_message),
    #     parse_mode='HTML'
    # )


def help_command_handler(update, context):
    """ Show available bot commands"""

    update.message.reply_text(
        orm_get_system_parameter(UI_bot_help_message),
        parse_mode='HTML'
    )

    # show custom commands
    # categories = orm_get_categories_valid_command()
    # msg = ''
    # for cat in categories:
    #     msg = msg + '/' + cat.custom_telegram_command + ' : ' + UI_message_receive_info_about_category.format(cat.name) + '\n'
    #
    # update.message.reply_text(
    #     msg,
    #     parse_mode='HTML'
    # )


def help_categories(update, context):
    categories = orm_get_categories_valid_command()
    msg = ''
    for cat in categories:
        msg = msg + '/' + cat.custom_telegram_command + ' : ' + UI_message_receive_info_about_category.format(cat.name) + '\n'

    update.message.reply_text(
        msg,
        parse_mode='HTML'
    )


def privacy_command_handler(update, context):
    telegram_user = orm_get_telegram_user(update.message.from_user.id)

    privacy_state = telegram_user.has_accepted_privacy_rules

    print("privacy_command_handler - user id=" + str(telegram_user.id) + " privacy accepted: " + str(privacy_state))

    if not privacy_state:
        #

        buttons = [[InlineKeyboardButton(text=UI_ACCEPT_UC, callback_data='privacy ' + UI_ACCEPT_UC),
                    InlineKeyboardButton(text=UI_NOT_ACCEPT_UC, callback_data='privacy ' + UI_NOT_ACCEPT_UC)]
                   ]

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=UI_message_read_and_accept_privacy_rules_as_follows + orm_get_system_parameter(UI_PRIVACY),
            reply_markup=InlineKeyboardMarkup(buttons)
        )

        return

    # https://stackoverflow.com/a/17311079/974287
    update.message.reply_text(
        UI_message_you_have_accepted_privacy_rules_on_this_day + (telegram_user.privacy_acceptance_timestamp.strftime(DATE_FORMAT_STR)),
        parse_mode='HTML'
    )


def undo_privacy_command_handler(update, context):
    orm_change_user_privacy_setting(update.message.from_user.id, False)

    print("undo_privacy_command_handler - telegram user id=" + str(update.message.from_user.id))

    update.message.reply_text(
        UI_message_your_privacy_acceptance_has_been_deleted,
        parse_mode='HTML'
    )

    pass


def detach_from_bot(update, context):
    # TODO: l'utente si scollega dal bot

    update.message.reply_text(
        'Ok! Bye!',
        parse_mode='HTML'
    )
    pass


def ask_age(update, context):
    # if DEBUG_MSG:
    #     print("ask_age update:")
    #     my_print(update, 4)

    telegram_user_id = update.callback_query.from_user.id

    # update.callback_query.edit_message_text(
    #     'Per fornirti un servizio migliore, ho bisogno di sapere la tua età.\nQuanti anni hai?',
    #     parse_mode='HTML'
    # )

    context.bot.send_message(
        chat_id=telegram_user_id,
        text='Per fornirti un servizio migliore, ho bisogno di sapere la tua età.\nQuanti anni hai?',
        parse_mode='HTML',
    )

    orm_set_telegram_user_expected_input(telegram_user_id, 'a')
    return


def ask_educational_level(update, context):
    telegram_user_id = update.message.chat.id

    keyboard = []

    for row in EDUCATIONAL_LEVELS:
        # print(row)
        keyboard.append([InlineKeyboardButton(
            text=row[1],
            callback_data='education_level ' + row[0])]
        )

    # keyboard.append(
    #     [InlineKeyboardButton(text=UI_CLOSE_UC, callback_data='choice OK')]
    # )

    context.bot.send_message(
        chat_id=telegram_user_id,
        text='Ultima cosa: per fornirti un servizio migliore, ho bisogno di sapere il tuo titolo di studio più elevato:',
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def callback_privacy(update, context, param):

    if DEBUG_MSG:
        print("callback_privacy update:")
        my_print(update, 4)

    telegram_user_id = update.callback_query.from_user.id

    if param == UI_ACCEPT_UC:
        privacy_setting = True
    else:
        privacy_setting = False

    orm_change_user_privacy_setting(telegram_user_id, privacy_setting)

    if privacy_setting:
        # message and buttons are replaced by this text
        update.callback_query.edit_message_text(
            UI_message_thank_you_for_accepting_privacy_rules, # + orm_get_system_parameter(UI_bot_help_message)
            parse_mode='HTML'
        )

        ask_age(update, context)
    else:
        update.callback_query.edit_message_text(
            text=UI_message_you_have_not_accepted_privacy_rules_cannot_continue)


# def callback_internship(update, context, param):
#     telegram_user_id = update.callback_query.from_user.id
#
#     if param == UI_OK:
#         intership_setting = True
#     else:
#         intership_setting = False
#
#     orm_change_user_intership_setting(telegram_user_id, intership_setting)
#
#     update.callback_query.edit_message_text(
#         UI_message_intership_settings_modified,
#         parse_mode='HTML'
#     )


# def process_intership_message(update, context, param):
#
#     if param == UI_message_ok_internship_info:
#         intership_setting = True
#     elif param == UI_message_no_internship_info:
#         intership_setting = False
#     else:
#         return False
#
#     telegram_user_id = update.message.chat.id
#
#     orm_change_user_intership_setting(telegram_user_id, intership_setting)
#
#     update.message.reply_text(
#         UI_message_intership_settings_modified_true if intership_setting else UI_message_intership_settings_modified_false,
#         parse_mode='HTML'
#     )
#
#     return True


def callback(update, context):
    """ Gestisce i callback_data inviati dalle inline_keyboard """

    data = update.callback_query.data.split()
    # I dati inviati dalle callback_query sono organizzati come segue:
    # il primo elemento contiente una stringa identificativa del contesto
    # il secondo elemento (e eventuali successivi) contiene i dati da passare

    keyword = data[0]

    print("callback " + keyword)

    if keyword == 'feedback':  # Callback per i feedback agli articoli
        callback_feedback(update, data[1:])

    elif keyword == 'comment':  # Callback per i commenti agli articoli
        callback_comment(update, context, data[1])

    elif keyword == 'choice':  # Callback per la scelta delle categorie
        callback_choice(update, data[1])

    elif keyword == 'privacy':
        callback_privacy(update, context, data[1])

    elif keyword == 'education_level':
        callback_education_level(update, context, data[1])


# SEZIONE SCELTA CATEGORIE
# ****************************************************************************************

def choose_news_categories(update, context):
    """ Permette all'utente di scegliere tra le categorie disponibili """

    telegram_user = orm_get_telegram_user(update.message.from_user.id)

    if check_user_is_enabled(telegram_user, update, context):
        return

    if check_user_privacy_approval(telegram_user, update, context):
        # privacy not yet approved by user
        return

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=orm_get_system_parameter(UI_select_news_categories),
        reply_markup=InlineKeyboardMarkup(inline_keyboard(telegram_user))
    )


def inline_keyboard(user):
    """ Costruisce la inline_keyboard in base alle categorie già scelte
    dall'utente passato per parametro """

    keyboard = []

    all_categories = orm_get_categories()

    # a = datetime.datetime.now()
    # test = list(set(all_categories.all()).difference(user.categories.all()))
    # b = datetime.datetime.now()
    # c = b - a
    # print("inline_keyboard(1) dt=" + str(c.microseconds) + " microseconds")
    # print(test)

    user_categories_set = set(user.categories.all())

    # a = datetime.datetime.now()
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
    # b = datetime.datetime.now()
    # c = b - a
    # print("inline_keyboard(2) dt=" + str(c.microseconds) + " microseconds")

    # add close button
    keyboard.append(
        [InlineKeyboardButton(text=UI_CLOSE_UC, callback_data='choice OK')]
    )

    return keyboard


def callback_education_level(update, context, choice: str):
    for line in EDUCATIONAL_LEVELS:
        if line[0] == choice:
            el = line[1]
            break

    telegram_user = orm_get_telegram_user(update.callback_query.from_user.id)

    print("callback_education_level: " + choice + " " + el)

    update.callback_query.edit_message_text(
        text='Grazie, hai scelto ' + el + ' come livello studio.\nOra sono pronto ad iniziare!'
    )

    orm_set_telegram_user_educational_level(telegram_user, choice)

    return


def callback_choice(update, choice: str):
    """ Gestisce i pulsanti premuti nella inline_keyboard """

    a = datetime.datetime.now()

    telegram_user = orm_get_telegram_user(update.callback_query.from_user.id)

    if choice == 'OK':  # 'OK'  Stampa le categorie scelte
        choosen_categories = telegram_user.categories_str()

        # ALERT: Non è stata scelta alcuna categoria!
        if choosen_categories == '':
            # update.callback_query.answer(
            #     text=UI_message_you_have_choosen_no_categories,
            #     show_alert=True
            # )
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
            text=orm_get_system_parameter(UI_select_news_categories),
            reply_markup=InlineKeyboardMarkup(inline_keyboard(telegram_user))
        )

    b = datetime.datetime.now()

    c = b - a

    print("callback_choice dt=" + str(c.microseconds) + " microseconds")


def _get_category_status(update, context, custom_telegram_command):
    telegram_user = orm_get_telegram_user(update.message.from_user.id)

    if check_user_privacy_approval(telegram_user, update, context):
        # privacy not yet approved by user
        return

    category = orm_lookup_category_by_custom_command(custom_telegram_command)

    if category is None:
        #
        return

    queryset = telegram_user.categories.filter(key=category.key)

    if len(queryset) == 0:
        return False
    else:
        return True


def _change_categories(update, context, category_group_name):
    telegram_user = orm_get_telegram_user(update.message.from_user.id)

    if check_user_privacy_approval(telegram_user, update, context):
        # privacy not yet approved by user
        return

    group = orm_get_category_group(category_group_name)

    if group is None:
        print("_change_categories - category group '" + category_group_name + "' is not defined")
        return

    telegram_user = orm_set_telegram_user_categories(update.message.chat.id, group.categories)

    update.message.reply_text(
        UI_message_i_have_changed_your_categories + telegram_user.categories_str(),
        parse_mode='HTML'
    )


def _set_all_categories(update, context, add_or_remove_all: bool):
    telegram_user = orm_get_telegram_user(update.message.from_user.id)

    if check_user_privacy_approval(telegram_user, update, context):
        # privacy not yet approved by user
        return

    if add_or_remove_all:
        queryset = orm_get_categories()

        telegram_user = orm_set_telegram_user_categories(update.message.chat.id, queryset)

        update.message.reply_text(
            UI_message_i_have_changed_your_categories + telegram_user.categories_str(),
            parse_mode='HTML'
        )
    else:
        telegram_user = orm_set_telegram_user_categories(update.message.chat.id, None)

        update.message.reply_text(
            UI_message_i_have_removed_all_your_categories ,
            parse_mode='HTML'
        )


def custom_command_handler(update, context):

    original_command = update.message.text

    print("custom_command_handler: " + original_command)

    telegram_user_id = update.message.chat.id
    telegram_user = orm_get_telegram_user(telegram_user_id)

    if check_user_is_enabled(telegram_user, update, context):
        return

    if check_user_privacy_approval(telegram_user, update, context):
        # privacy not yet approved by user
        return

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

    msg = (UI_message_you_are_subscribed_to_news_category if status else UI_message_you_are_not_subscribed_to_news_category).format(cat.name)

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


# def process_custom_telegram_command(update, context, param):
#
#     if param.endswith(UI_message_ok_suffix):
#         custom_telegram_command = param[:len(param) - len(UI_message_ok_suffix)]
#         category_setting = True
#     elif param.endswith(UI_message_no_suffix):
#         custom_telegram_command = param[:len(param) - len(UI_message_no_suffix)]
#         category_setting = False
#     else:
#         return False
#
#     # print(custom_telegram_command)
#
#     telegram_user_id = update.message.chat.id
#
#     res = orm_change_user_custom_setting(telegram_user_id, custom_telegram_command, category_setting)
#
#     if res:
#         update.message.reply_text(
#             (UI_message_custom_settings_modified_true if category_setting else UI_message_custom_settings_modified_false).format(custom_telegram_command),
#             parse_mode='HTML'
#         )
#         return True
#     else:
#         return False


# TODO mostrare quante news (nell'ultima settimana) l'utente avrebbe ricevuto, con questi settings


def all_categories_command_handler(update, context):
    _set_all_categories(update, context, True)


def no_categories_command_handler(update, context):
    _set_all_categories(update, context, False)


# def internship_command_handler(update, context):
#     intership_ok_keyboard = telegram.KeyboardButton(text=UI_message_ok_internship_info)
#     intership_no_keyboard = telegram.KeyboardButton(text=UI_message_no_internship_info)
#
#     custom_keyboard = [[intership_ok_keyboard, intership_no_keyboard]]
#
#     reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True, one_time_keyboard=True)
#
#     update.message.reply_text(
#         UI_message_receive_internship_question,
#         parse_mode='HTML',
#         reply_markup=reply_markup
#     )


def me_command_handler(update, context):

    telegram_user = orm_get_telegram_user(update.message.from_user.id)

    if check_user_privacy_approval(telegram_user, update, context):
        # privacy not yet approved by user
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


def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


def news_dispatcher(context: CallbackContext):
    a = datetime.datetime.now()

    list_of_news = orm_get_fresh_news_to_send()

    debug_send_news = (orm_get_system_parameter("DEBUG_SEND_NEWS").lower() == "true")
    if debug_send_news:
        print("DEBUG_SEND_NEWS = " + str(debug_send_news))

    now = datetime.datetime.now()

    if len(list_of_news) == 0:
        print("news_dispatcher - nothing to do " + str(now))
        return
    else:
        print("news_dispatcher - there are news to process: " + str(len(list_of_news)))

    all_telegram_users = orm_get_all_telegram_users()

    for news_item in list_of_news:

        print("news_dispatcher - elaboration of news item id=" + str(news_item.id))

        for telegram_user in all_telegram_users:

            if not telegram_user.enabled:
                continue

            intersection_result = intersection(news_item.categories.all(), telegram_user.categories.all())

            if news_item.broadcast_message is not True and len(intersection_result) == 0:
                continue

            # send this news to this telegram_user
            send_news_to_telegram_user(context, news_item, telegram_user, intersection_result)

        news_item.processed = True
        from django.utils.timezone import now
        news_item.processed_timestamp = now()
        if not debug_send_news:
            news_item.save()

    b = datetime.datetime.now()

    c = b - a

    print("news_dispatcher - finished processing all news - dt=" + str(c.microseconds) + " microseconds")


# SEZIONE INVIO NEWS
# ****************************************************************************************

def send_news_to_telegram_user(context, news_item : NewsItem, telegram_user: TelegramUser, intersection_result, request_feedback=True,
                               title_only=False, ask_comment=False):
    print(
        "send_news_to_telegram_user - news_item=" + str(news_item.id) + ", telegram_user=" + str(telegram_user.user_id))

    a = datetime.datetime.now()

    # build html content

    # title_html_content = ''
    categories_html_content = ''
    body_html_content = ''
    link_html_content = ''

    # see also: https://core.telegram.org/bots/api#html-style
    # cannot embed <b> inside <a> tag

    if news_item.processed and news_item.processed_timestamp is not None:
        processed_timestamp_html = ' ' + news_item.processed_timestamp.strftime(DATE_FORMAT_STR)
    else:
        processed_timestamp_html = ''

    # title/header
    if news_item.title_link is not None:
        title_html_content = '<a href="' + news_item.title_link + '"> ' + \
                             str(news_item.title) + \
                             ' [' + str(news_item.id) + ']' + processed_timestamp_html + \
                                                        ' </a>\n'
    else:
        title_html_content = '<b>' + str(news_item.title) + \
                             ' [' + str(news_item.id) + ']' + processed_timestamp_html + '</b>\n'

    show_categories_in_news = orm_get_system_parameter(param_show_match_category_news).lower() == "true"

    # optional: show categories
    if show_categories_in_news is True:
        if intersection_result is not None:
            # print(intersection_result)
            categories_html_content = '\n<i>'

            for cat in intersection_result:
                categories_html_content += cat.name + ','

            categories_html_content = categories_html_content[:-1]

            categories_html_content += '</i>\n'
        elif news_item.broadcast_message is True:
            categories_html_content = '\n<i>' + UI_broadcast_message + '</i>\n'

    # news body
    news_text = news_item.text

    if news_text is not None:
        if news_item.show_all_text:
            body_html_content = news_text
        else:
            text = news_text.split()

            number_of_words = news_item.show_first_n_words
            if number_of_words < 0:
                number_of_words = 30

            body_html_content = str(" ".join(text[:number_of_words]))

    # optional link
    if news_item.link is not None:
        link_html_content = '... <a href=\"' + news_item.link + '\">' + news_item.link_caption + '</a>'

    html_content = title_html_content + categories_html_content + body_html_content + link_html_content

    print("send_news_to_telegram_user - len(html_content) = " + str(len(html_content)))

    # print("len(title_html_content) = " + str(len(title_html_content)))
    # print("len(categories_html_content) = " + str(len(categories_html_content)))
    # print("len(body_html_content) = " + str(len(body_html_content)))
    # print("len(link_html_content) = " + str(len(link_html_content)))

    if news_item.file1 is not None:
        # print(news_item.file1.file_field.name)
        # example: uploads/2019/10/03/500px-Tux_chico.svg_VtRyDrN.png

        image_path = MEDIA_ROOT + news_item.file1.file_field.name

        print("send_news_to_telegram_user - fs path of image to send: " + image_path)

        # LIMIT on caption len: 1024 bytes! or we get MEDIA_CAPTION_TOO_LONG from Telegram
        # https://core.telegram.org/bots/api#sendphoto

        if len(html_content) > 1024:
            # print("reducing html_content, too long!")
            # html_content = html_content[:1024]
            context.bot.send_photo(
                chat_id=telegram_user.user_id,
                photo=open(image_path, 'rb'),
                caption='',
                parse_mode='HTML'
            )
            context.bot.send_message(
                chat_id=telegram_user.user_id,
                text=html_content,
                parse_mode='HTML'
            )
        else:
            context.bot.send_photo(
                chat_id=telegram_user.user_id,
                photo=open(image_path, 'rb'),
                caption=html_content,
                parse_mode='HTML'
            )
    else:

        context.bot.send_message(
            chat_id=telegram_user.user_id,
            text=html_content,
            parse_mode='HTML'
        )

    if news_item.file2 is not None:
        file_path = MEDIA_ROOT + news_item.file2.file_field.name
        print("send_news_to_telegram_user - fs path of file2 to send: " + file_path)

        context.bot.send_document(
            chat_id=telegram_user.user_id,
            document=open(file_path, 'rb'),
            caption='',
            parse_mode='HTML'
        )

    if news_item.file3 is not None:
        file_path = MEDIA_ROOT + news_item.file3.file_field.name
        print("send_news_to_telegram_user - fs path of file3 to send: " + file_path)

        context.bot.send_document(
            chat_id=telegram_user.user_id,
            document=open(file_path, 'rb'),
            caption='',
            parse_mode='HTML'
        )

    # keyboard with 'like' and 'dislike' buttons
    if request_feedback:
        context.bot.send_message(
            chat_id=telegram_user.user_id,
            text=orm_get_system_parameter(UI_request_for_news_item_feedback),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(  # dislike button
                    text=u'\u2717',
                    callback_data='feedback - ' + str(news_item.id) + ' ' + str(ask_comment)
                ),
                InlineKeyboardButton(  # like button
                    text=u'\u2713',
                    callback_data='feedback + ' + str(news_item.id) + ' ' + str(ask_comment)
                )
            ]])
        )

    orm_log_news_sent_to_user(news_item, telegram_user)


    orm_inc_telegram_user_number_received_news_items(telegram_user)

    b = datetime.datetime.now()

    c = b - a

    print("send_news_to_telegram_user - dt=" + str(c.microseconds) + " microseconds")


def resend_last_processed_news(update, context):
    print("resend_last_processed_news")
    # print(update)
    telegram_user_id = update.message.chat.id
    telegram_user = orm_get_telegram_user(telegram_user_id)

    if check_user_is_enabled(telegram_user, update, context):
        return

    if check_user_privacy_approval(telegram_user, update, context):
        # privacy not yet approved by user
        return

    now = datetime.datetime.now()

    if telegram_user.resend_news_timestamp is not None and telegram_user.resend_news_timestamp > now - datetime.timedelta(hours=1):
        print("resend_last_processed_news: too frequent! skipping")
        return

    telegram_user.resend_news_timestamp = now
    orm_update_telegram_user(telegram_user)

    news_query = orm_get_last_processed_news()

    print("resend_last_processed_news - processed news items= " + str(len(news_query)))

    if len(news_query) == 0:
        context.bot.send_message(
            chat_id=telegram_user.user_id,
            text=UI_message_no_previous_news_to_send_again,
            parse_mode='HTML'
        )
        return

    telegram_user_categories = telegram_user.categories.all()

    counter = 0

    for news_item in reversed(news_query[:5]):

        intersection_result = intersection(news_item.categories.all(), telegram_user_categories)

        if news_item.broadcast_message is not True and len(intersection_result) == 0:
            continue

        print("resend_last_processed_news - sending news_item.id=" + str(news_item.id))

        send_news_to_telegram_user(context, news_item, telegram_user, intersection_result=intersection_result,
                                   request_feedback=False, title_only= True)

        counter = counter + 1

    if counter == 0:
        context.bot.send_message(
            chat_id=telegram_user.user_id,
            text=UI_message_no_matching_previous_news,
            parse_mode='HTML'
        )


# def news(update, context):
#     """ Invia un nuovo articolo """
#
#     folder_new = '/home/marco/Documents/github/dclavorofvg-bot/demo_new'
#
#     # fd = open(folder_new + '/category', 'r')
#     # cat = fd.read()[:-1]
#
#     fd = open(folder_new + '/title', 'r')
#     title = fd.read()[:-1]
#
#     fd = open(folder_new + '/body', 'r')
#     body = fd.read()
#
#     fd = open(folder_new + '/link', 'r')
#     link = fd.read()
#     fd.close()
#
#     news_item = orm_add_newsitem(title, body, link)
#     context.user_data['news_id'] = news_item.id
#
#     # Costruzione della descrizione
#     caption = '<b>' + str(news_item.title) + \
#               ' [' + news_item.id + ']</b>\n'
#
#     text = news_item.text.split()
#     caption += str(" ".join(text[:30]))
#
#     # Aggiunta del link per approfondire
#     caption += '... <a href=\"' + news_item.link + '\">continua</a>'
#
#     context.bot.send_photo(
#         chat_id=update.message.chat_id,
#         photo=open(folder_new + '/allegato_1.jpg', 'rb'),
#         caption=caption,
#         parse_mode='HTML'
#     )
#
#     # Attivazione tastiera con pulsanti 'like' e 'dislike'
#     context.bot.send_message(
#         chat_id=update.message.chat_id,
#         text="Ti è piaciuto l'articolo?",
#         reply_markup=InlineKeyboardMarkup([[
#             InlineKeyboardButton(  # Pulsante dislike
#                 text=u'\u2717',
#                 callback_data='feedback - ' + news_item.id
#             ),
#             InlineKeyboardButton(  # Pulsante like
#                 text=u'\u2713',
#                 callback_data='feedback + ' + news_item.id
#             )
#         ]])
#     )


def debug_command_handler(update, context):

    telegram_user_id = update.message.chat.id
    telegram_user = orm_get_telegram_user(telegram_user_id)

    if check_user_is_enabled(telegram_user, update, context):
        return

    if not telegram_user.is_admin:
        return

    # debug only
    print("debug_command_handler")
    news_dispatcher(context)
    pass


def debug2_command_handler(update, context):

    telegram_user_id = update.message.chat.id
    telegram_user = orm_get_telegram_user(telegram_user_id)

    if check_user_is_enabled(telegram_user, update, context):
        return

    if not telegram_user.is_admin:
        return

    print("debug2_command_handler")

    orm_change_user_privacy_setting(telegram_user_id, False)

    pass


def callback_feedback(update, data):
    """ Gestisce i feedback sugli articoli """

    feed = data[0]
    news_id = data[1]
    orm_add_feedback(feed, news_id, update.callback_query.message.chat.id)  # Aggiunge il nuovo feedback

    # Attivazione tastiera con pulsante 'commenta'
    update.callback_query.edit_message_text(
        text=UI_message_thank_you_for_feedback,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(
                text=UI_message_write_a_comment,
                callback_data='comment ' + news_id)]
        ])
    )


def callback_comment(update, context, news_id):
    """ Gestisce i commenti agli articoli """
    print("callback_comment")

    # Rimuove il pulsante 'commenta'
    update.callback_query.edit_message_text(
        UI_message_thank_you_for_feedback
    )

    # Invia un messaggio con i dati dell'articolo da commentare
    context.bot.send_message(
        chat_id=update.callback_query.message.chat_id,
        text=UI_message_comment_to_news_item.format(news_id),
        reply_markup=ForceReply()  # Invita l'utente a rispondere al messaggio
    )


def comment_handler(update, context):
    """ Memorizza il commento inserito dall'utente """

    # Testo del messaggio cui il commento fornisce una risposta
    # (c'è il codice dell'articolo)
    reply_data = update.message.reply_to_message.text.split()
    # print(reply_data)
    orm_add_comment(update.message.text, reply_data[3], update.message.chat.id)

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=UI_message_comment_successful
    )


def generic_message_handler(update, context):
    if DEBUG_MSG:
        print("generic_message_handler update:")
        my_print(update, 4)

    message_text = update.message.text

    print("generic_message_handler - message_text = " + message_text)

    telegram_user_id = update.message.chat.id
    print(telegram_user_id)
    telegram_user = orm_get_telegram_user(telegram_user_id)

    if check_user_is_enabled(telegram_user, update, context):
        return

    if check_user_privacy_approval(telegram_user, update, context):
        # privacy not yet approved by user
        return

    # if process_custom_telegram_command(update, context, message_text):
    #     return

    # if process_intership_message(update, context, message_text):
    #     return
    # elif process_courses_message(update, context, message_text):
    #     return
    # elif process_recruiting_day_message(update, context, message_text):
    #     return

    expected_input = orm_get_user_expected_input(telegram_user)

    if expected_input == 'a':
        # expecting age from user
        if orm_parse_user_age(telegram_user, message_text):
            # update.message.reply_text(
            #     UI_message_thank_you,
            #     parse_mode='HTML'
            # )

            # now ask educational level
            ask_educational_level(update, context)

            return

    if message_text.lower() in help_keyword_list or len(message_text) <= 2:
        update.message.reply_text(
            orm_get_system_parameter(UI_bot_help_message),
            parse_mode='HTML'
        )
    else:
        global_bot_instance.send_chat_action(chat_id=telegram_user_id, action=ChatAction.TYPING)


# def callback_minute(context: telegram.ext.CallbackContext):
#     all_telegram_users = orm_get_all_telegram_users()
#
#     for telegram_user in all_telegram_users:
#         print("*** " + str(telegram_user.user_id))
#
#         context.bot.send_message(chat_id=telegram_user.user_id,
#                                  text='One message every 10 minutes')


class MQBot(Bot):
    '''A subclass of Bot which delegates send method handling to MQ'''

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
    print("***error_callback***")
    print(update)
    print(error)

    try:
        raise error
    except Unauthorized:
        # remove update.message.chat_id from conversation list
        print(error)
        logging.error("Unauthorized")
    except BadRequest:
        # handle malformed requests - read more below!
        print(error)
        logging.error("BadRequest")
    except TimedOut:
        # handle slow connection problems
        print(error)
        logging.error("TimedOut")
    except NetworkError:
        # handle other connection problems
        print(error)
        logging.error("NetworkError")
    except ChatMigrated as e:
        # the chat_id of a group has changed, use e.new_chat_id instead
        print(error)
        logging.error("ChatMigrated")
    except TelegramError:
        # handle all other telegram related errors
        print(error)
        logging.error("TelegramError")


# ****************************************************************************************
def main():
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

    # upd = telegram.ext.updater.Updater(bot=testbot)

    updater = Updater(bot=my_bot, use_context=True)  # removed: token=token
    dp = updater.dispatcher

    job_queue = updater.job_queue

    job_minute = job_queue.run_repeating(news_dispatcher, interval=60 * 5, first=0)  # callback_minute

    # Handler per servire TUTTE le inline_keyboard
    dp.add_handler(CallbackQueryHandler(callback))

    # Aggiunta dei vari handler
    dp.add_handler(CommandHandler(UI_START_COMMAND, start_command_handler))

    if UI_START_COMMAND_ALT is not None:
        dp.add_handler(CommandHandler(UI_START_COMMAND_ALT, start_command_handler))

    dp.add_handler(CommandHandler(UI_HELP_COMMAND, help_command_handler))

    if UI_HELP_COMMAND_ALT is not None:
        dp.add_handler(CommandHandler(UI_HELP_COMMAND_ALT, help_command_handler))

    dp.add_handler(CommandHandler(UI_PRIVACY_COMMAND, privacy_command_handler))
    dp.add_handler(CommandHandler(UI_UNDO_PRIVACY_COMMAND, undo_privacy_command_handler))

    # categories = orm_get_categories_valid_command()
    # for cat in categories:
    #     dp.add_handler(CommandHandler(cat.custom_telegram_command, unknown_command_handler))

    # dp.add_handler(CommandHandler(UI_VACANCIES_COMMAND, vacancies_command_handler))
    # dp.add_handler(CommandHandler(UI_YOUNG_COMMAND, young_categories_command_handler))

    # these are 'standard' commands (add all categories / remove all categories)
    dp.add_handler(CommandHandler(UI_ALL_CATEGORIES_COMMAND, all_categories_command_handler))
    dp.add_handler(CommandHandler(UI_NO_CATEGORIES_COMMAND, no_categories_command_handler))

    # dp.add_handler(CommandHandler(UI_INTERNSHIP_COMMAND, internship_command_handler))
    # dp.add_handler(CommandHandler(UI_COURSES_COMMAND, courses_command_handler))
    # dp.add_handler(CommandHandler(UI_RECRUITING_DAY_COMMAND, recruiting_day_command_handler))

    dp.add_handler(CommandHandler(UI_ME_COMMAND, me_command_handler))

    #
    dp.add_handler(CommandHandler(UI_DETACH_BOT, detach_from_bot))

    # Handlers per la sezione INVIO NEWS
    dp.add_handler(CommandHandler(UI_RESEND_LAST_NEWS_COMMAND, resend_last_processed_news))
    dp.add_handler(MessageHandler(Filters.reply, comment_handler))
    dp.add_handler(MessageHandler(Filters.text, generic_message_handler))

    # Handlers per la sezione SCELTA CATEGORIE
    dp.add_handler(CommandHandler(UI_CHOOSE_CATEGORIES_COMMAND, choose_news_categories))

    dp.add_handler(CommandHandler(UI_CATEGORIES_HELP, help_categories))

    dp.add_handler(CommandHandler(UI_DEBUG_COMMAND, debug_command_handler))
    dp.add_handler(CommandHandler(UI_DEBUG2_COMMAND, debug2_command_handler))

    # catch all unknown commands (including custom commands associated to categories)
    dp.add_handler(MessageHandler(Filters.command, custom_command_handler))

    # https://github.com/python-telegram-bot/python-telegram-bot/wiki/Exception-Handling
    dp.add_error_handler(error_callback)

    # Avvio l'updater
    updater.start_polling()

    # Arresta il bot in caso sia stato premuto Ctrl+C o il processo abbia ricevuto SIGINT, SIGTERM o SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
