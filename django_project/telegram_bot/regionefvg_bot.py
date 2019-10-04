import os

# cd Scrivania/regionefvg_bot
# export PYTHONPATH=.:django_project/telegram_bot
# python django_project/telegram_bot/regionefvg_bot.py

from django_project.telegram_bot.ormlayer import *

try:
    from ..backoffice.definitions import UI_presentazione_bot, UI_bot_help_message
except:
    from django_project.backoffice.definitions import UI_presentazione_bot, UI_bot_help_message

from telegram.ext import *
from telegram import *

import telegram.bot
from telegram.ext import messagequeue as mq

import logging

from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)

from django_project.gfvgbo.settings import MEDIA_ROOT

# Spiega quando (e perché) le cose non funzionano come ci si aspetta
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# ****************************************************************************************
# return True if user has not yet approved the bot's privacy policy
def check_user_privacy_approval(telegram_user, update, context):
    if not telegram_user.has_accepted_privacy_rules:
        print("*** PRIVACY NOT APPROVED ***")

        update.message.reply_text(
            'Prima di proseguire, devi accettare il regolamento per la /privacy di questo bot.\n'
            'Usa il comando /privacy per visualizzare il regolamento.'
        )
        return True

    return False


def start(update, context):
    """ Registra l'utente, nel caso sia al primo accesso; mostra i comandi disponibili """

    print(context.args)  # parametro via start; max 64 caratteri
    # https://telegram.me/marcotts_bot?start=12345

    telegram_user = orm_add_user(update.message.from_user)  # orm_add_user always returns a TelegramUser instance

    presentazione_bot = orm_get_system_parameter(UI_presentazione_bot)

    update.message.reply_text(
        'Ciao ' + update.message.from_user.first_name + '! ' + presentazione_bot
    )

    # if check_user_privacy_approval(telegram_user, update, context):
    if not telegram_user.has_accepted_privacy_rules:
        # privacy not yet approved by user
        return privacy(update, context)

    update.message.reply_text(
        orm_get_system_parameter(UI_bot_help_message),
        parse_mode='HTML'
    )


def help(update, context):
    """ Mostra i comandi disponibili """

    update.message.reply_text(
        orm_get_system_parameter(UI_bot_help_message),
        parse_mode='HTML'
    )


def privacy(update, context):
    user = orm_get_telegram_user(update.message.from_user.id)

    privacy_state = user.has_accepted_privacy_rules

    print("privacy - " + str(user) + " " + str(privacy_state))

    if not privacy_state:
        #

        buttons = [[InlineKeyboardButton(text='ACCETTO', callback_data='privacy ACCETTO'),
                    InlineKeyboardButton(text='NON ACCETTO', callback_data='privacy NON_ACCETTO')]
                   ]

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Per proseguire con l'utilizzo di questo bot, "
                 "è necessario che tu legga ed accetti il regolamento sulla privacy qui di seguito riportato:\n"
                 + orm_get_privacy_rules(),
            reply_markup=InlineKeyboardMarkup(buttons)
        )

        return

    update.message.reply_text(
        'hai accettato il regolamento della privacy di questo bot in data ' + str(user.privacy_acceptance_timestamp),
        parse_mode='HTML'
    )


def detach_from_bot(update, context):
    # TODO: l'utente si scollega dal bot

    update.message.reply_text(
        'Ok! Bye!',
        parse_mode='HTML'
    )
    pass


def callback_privacy(update, context, param):
    id_utente = update.callback_query.from_user.id
    # print("callback_privacy - id_utente = " + str(id_utente))

    if param == "ACCETTO":
        privacy_setting = True
    else:
        privacy_setting = False

    orm_change_user_privacy_setting(id_utente, privacy_setting)

    if privacy_setting:
        # comandi a disposizione
        update.callback_query.edit_message_text(
            "Grazie per avere accettato il regolamento della privacy di questo bot.\n" +
            orm_get_system_parameter(UI_bot_help_message),
            parse_mode='HTML'
        )
    else:

        update.callback_query.edit_message_text(text="ok impostazione privacy = " + param)


def callback(update, context):
    """ Gestisce i callback_data inviati dalle inline_keyboard """

    data = update.callback_query.data.split()
    # I dati inviati dalle callback_query sono organizzati come segue:
    # il primo elemento contiente una stringa identificativa del contesto
    # il secondo elemento (e eventuali successivi) contiene i dati da passare

    if data[0] == 'feedback':  # Callback per i feedback agli articoli
        callback_feedback(update, data[1:])

    elif data[0] == 'comment':  # Callback per i commenti agli articoli
        callback_comment(update, context, data[1])

    elif data[0] == 'choice':  # Callback per la scelta delle categorie
        callback_choice(update, data[1])

    elif data[0] == 'privacy':
        callback_privacy(update, context, data[1])


# SEZIONE SCELTA CATEGORIE
# ****************************************************************************************

def choose_news_categories(update, context):
    """ Permette all'utente di scegliere tra le categorie disponibili """

    user = orm_get_telegram_user(update.message.from_user.id)

    if check_user_privacy_approval(user, update, context):
        # privacy not yet approved by user
        return

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=orm_get_system_parameter("UI seleziona le categorie di news"),
        reply_markup=InlineKeyboardMarkup(inline_keyboard(user))
    )


def inline_keyboard(user):
    """ Costruisce la inline_keyboard in base alle categorie già scelte
    dall'utente passato per parametro """

    keyboard = []

    all_categories = orm_get_categories()

    for cat in all_categories:
        queryset = user.categories.filter(key=cat.key)

        label = cat.name + ' ' + cat.emoji

        if len(queryset) != 0:
            label = u'\U00002705' + ' ' + label.upper()
        else:
            label = u'\U0000274C' + ' ' + label

        keyboard.append([InlineKeyboardButton(
            text=label,
            callback_data='choice ' + cat.key)]
            )

    # add close button
    keyboard.append(
        [InlineKeyboardButton(text='CHIUDI', callback_data='choice OK')]
    )

    return keyboard


def callback_choice(update, scelta):
    """ Gestisce i pulsanti premuti nella inline_keyboard """

    a = datetime.datetime.now()

    telegram_user = orm_get_telegram_user(update.callback_query.from_user.id)

    if scelta == 'OK':  # 'OK'  Stampa le categorie scelte
        cat_scelte = ''

        all_categories = orm_get_categories()

        for cat in all_categories:
            queryset = telegram_user.categories.filter(key=cat.key)
            if len(queryset) != 0:
                cat_scelte += '- ' + cat.name + \
                              '  ' + cat.emoji + '\n'

        # ALERT: Non è stata scelta alcuna categoria!
        if cat_scelte == '':
            update.callback_query.answer(
                text='Non è stata scelta alcuna categoria!',
                show_alert=True
            )
            return

        update.callback_query.edit_message_text(
            text='Grazie, hai scelto le seguenti categorie:\n\n' + cat_scelte +
                 '\nPuoi modificarle in qualsiasi momento usando il comando /scegli .'
        )

    else:  # Toggle checked/unchecked per la categoria selezionata
        update_user_category_settings(telegram_user, scelta)

        update.callback_query.edit_message_text(
            text="Seleziona una o più categorie:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard(telegram_user))
        )

    b = datetime.datetime.now()

    c = b - a

    print("callback_choice dt=" + str(c.microseconds) + " microseconds")


def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


def news_dispatcher(context: telegram.ext.CallbackContext):
    a = datetime.datetime.now()

    list_of_news = orm_get_news_to_process()

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

            if len(intersection_result) == 0:
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

def send_news_to_telegram_user(context, news_item, telegram_user, intersection_result, request_feedback=True):

    print("send_news_to_telegram_user - news_item=" + str(news_item.id) + ", telegram_user=" + str(telegram_user.user_id))

    a = datetime.datetime.now()

    # build html content

    # title_html_content = ''
    categories_html_content = ''
    body_html_content = ''
    link_html_content = ''

    # see also: https://core.telegram.org/bots/api#html-style
    # cannot embed <b> inside <a> tag

    # title/header
    if news_item.title_link is not None:
        title_html_content = '<a href="' + news_item.title_link + '"> ' + \
                  str(news_item.title) + \
                  ' [' + str(news_item.id) + ']' \
                  ' </a>\n'
    else:
        title_html_content = '<b>' + str(news_item.title) + \
            ' [' + str(news_item.id) + ']</b>\n'

    # optional: show categories
    if intersection_result is not None and orm_get_system_parameter("news - mostra match categoria").lower() == "true":
        # print(intersection_result)
        categories_html_content = '\n<i>'

        for cat in intersection_result:
            categories_html_content += cat.name + ','

        categories_html_content = categories_html_content[:-1]

        categories_html_content += '</i>\n'

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
            caption=html_content,
            parse_mode='HTML'
        )

    if news_item.file3 is not None:
        file_path = MEDIA_ROOT + news_item.file3.file_field.name
        print("send_news_to_telegram_user - fs path of file3 to send: " + file_path)

        context.bot.send_document(
            chat_id=telegram_user.user_id,
            document=open(file_path, 'rb'),
            caption=html_content,
            parse_mode='HTML'
        )

    # keyboard with 'like' and 'dislike' buttons
    if request_feedback:
        context.bot.send_message(
            chat_id=telegram_user.user_id,
            text=orm_get_system_parameter(UI_request_for_news_item_feedback),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(  # Pulsante dislike
                    text=u'\u2717',
                    callback_data='feedback - ' + str(news_item.id)
                ),
                InlineKeyboardButton(  # Pulsante like
                    text=u'\u2713',
                    callback_data='feedback + ' + str(news_item.id)
                )
            ]])
        )

    orm_log_news_sent_to_user(news_item, telegram_user)

    b = datetime.datetime.now()

    c = b - a

    print("send_news_to_telegram_user - dt=" + str(c.microseconds) + " microseconds")


def send_last_processed_news(update, context):
    print("send_last_processed_news")
    # print(update)

    telegram_user = orm_get_telegram_user(update.message.chat.id)

    # print(telegram_user)

    news_query = orm_get_last_processed_news()

    # TODO:
    # match with user categories

    print("send_last_processed_news - processed news items= " + str(len(news_query)))

    for news_item in news_query[:5]:

        print("***send_last_processed_news - sending " + str(news_item.id))

        send_news_to_telegram_user(context, news_item, telegram_user, intersection_result=None, request_feedback=False)


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


def debug_method(update, context):
    # debug only
    print("debug_method")
    news_dispatcher(context)
    pass


def callback_feedback(update, data):
    """ Gestisce i feedback sugli articoli """

    feed = data[0]
    news_id = data[1]
    orm_add_feedback(feed, news_id)  # Aggiunge il nuovo feedback

    # Attivazione tastiera con pulsante 'commenta'
    update.callback_query.edit_message_text(
        text='Grazie per il feedback!\n',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(
                text='Scrivi un commento',
                callback_data='comment ' + news_id)]
        ])
    )


def callback_comment(update, context, news_id):
    """ Gestisce i commenti agli articoli """

    # Rimuove il pulsante 'commenta'
    update.callback_query.edit_message_text(
        'Grazie per il feedback!'
    )

    # Invia un messaggio con i dati dell'articolo da commentare
    context.bot.send_message(
        chat_id=update.callback_query.message.chat_id,
        text='Commento art. ' + news_id,
        reply_markup=ForceReply()  # Invita l'utente a rispondere al messaggio
    )


def comment_handler(update, context):
    """ Memorizza il commento inserito dall'utente """

    # Testo del messaggio cui il commento fornisce una risposta
    # (c'è il codice dell'articolo)
    reply_data = update.message.reply_to_message.text.split()
    orm_add_comment(update.message.text, reply_data[2], update.message.from_user.id)

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Commento caricato con successo!'
    )


def generic_message_handler(update, context):

    # print("generic_message_handler - " + str(update))

    message_text = update.message.text

    print("generic_message_handler - message_text = " + message_text)

    # context.bot.send_message(
    #     chat_id=update.message.chat_id,
    #     text='hai bisogno di aiuto?'
    # )

    update.message.reply_text(
        orm_get_system_parameter(UI_bot_help_message),
        parse_mode='HTML'
    )


def callback_minute(context: telegram.ext.CallbackContext):
    all_telegram_users = orm_get_all_telegram_users()

    for telegram_user in all_telegram_users:
        print("*** " + str(telegram_user.user_id))

        context.bot.send_message(chat_id=telegram_user.user_id,
                                 text='One message every 10 minutes')


class MQBot(telegram.bot.Bot):
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

    # upd = telegram.ext.updater.Updater(bot=testbot)

    updater = Updater(bot=my_bot, use_context=True)  # removed: token=token
    dp = updater.dispatcher

    job_queue = updater.job_queue

    job_minute = job_queue.run_repeating(news_dispatcher, interval=60*5, first=0)  # callback_minute

    # Aggiunta dei vari handler
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('inizia', start))

    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('aiuto', help))
    dp.add_handler(CommandHandler('privacy', privacy))

    dp.add_handler(CommandHandler('lavoro', lavoro_command_handler))
    dp.add_handler(CommandHandler('offerte_di_lavoro', privacy))

    dp.add_handler(CommandHandler('fine', detach_from_bot))

    # Handlers per la sezione INVIO NEWS
    dp.add_handler(CommandHandler('invia_ultime_news', send_last_processed_news))  # DEBUG only
    dp.add_handler(MessageHandler(Filters.reply, comment_handler))
    dp.add_handler(MessageHandler(Filters.text, generic_message_handler))

    # Handlers per la sezione SCELTA CATEGORIE
    dp.add_handler(CommandHandler('scegli', choose_news_categories))

    dp.add_handler(CommandHandler('debug', debug_method))

    # Handler per servire TUTTE le inline_keyboard
    dp.add_handler(CallbackQueryHandler(callback))

    # https://github.com/python-telegram-bot/python-telegram-bot/wiki/Exception-Handling
    dp.add_error_handler(error_callback)

    # Avvio l'updater
    updater.start_polling()

    # Arresta il bot in caso sia stato premuto Ctrl+C o il processo abbia ricevuto SIGINT, SIGTERM o SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
