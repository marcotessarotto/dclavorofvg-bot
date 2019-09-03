import time
import datetime

import telegram

# cd /home/marco/Documents/github/giovanifvg-bot
# export PYTHONPATH=/home/marco/Documents/github/giovanifvg-bot/:/home/marco/Documents/github/giovanifvg-bot/gfvgbo/telegrambot/
# python /home/marco/Documents/github/giovanifvg-bot/gfvgbo/telegrambot/telegrambot.py

from gfvgbo.telegrambot.ormlayer import orm_add_user, update_user_keyword_settings, orm_get_user, orm_get_default_keywords_dict

from gfvgbo.backoffice.definitions import get_categories_dict

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler
)

import logging

# Spiega quando (e perché) le cose non funzionano come ci si aspetta
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)



category = get_categories_dict()

# pip install python-telegram-bot==12.0.0 --upgrade


comandi_disponibili = "/help oppure /aiuto\n" \
                      "/start\n" \
                      "/mandami_ultima_newsletter\n" \
                      "/voglio_ricevere_newsletter\n" \
                      "/condividi_posizione\n" \
                      "/scegli_categorie"


# https://github.com/python-telegram-bot/python-telegram-bot/wiki/Avoiding-flood-limits
# inviare un msg ogni 40 ms


def print_timestamp():
    ts = time.time()

    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    print(st)


def condividi_posizione(update, context):
    chat_id = update.message.chat_id

    location_keyboard = telegram.KeyboardButton(text="send_location", request_location=True)
    contact_keyboard = telegram.KeyboardButton(text="send_contact", request_contact=True)
    custom_keyboard = [[location_keyboard, contact_keyboard]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    context.bot.send_message(chat_id=chat_id,
                             text="Would you mind sharing your location and contact with me?",
                             reply_markup=reply_markup)

    update.message.reply_text(
        'Ciao {}'.format(update.message.from_user.first_name))


def hello(update, context):
    chat_id = update.message.chat_id

    print("hello 123")

    context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)


def start(update, context):
    print(context.args)  # parametro via start; max 64 caratteri
    # https://telegram.me/marcotts_bot?start=12345

    print(update.message.from_user)
    django_user = orm_add_user(update.message.from_user)
    print("result from orm_add_user: " + str(django_user))

    update.message.reply_text(
        'Ciao {}, benvenuto al servizio GiovaniFVG,\nhai a disposizione i seguenti comandi:\n'.format(
            update.message.from_user.first_name + " pk=" + str(django_user.id)) + comandi_disponibili)


def help(update, context):
    update.message.reply_text('comandi:\n' + comandi_disponibili)


def alarm(context):
    """Send the alarm message."""
    print_timestamp()
    print("ora manderò una newsletter all'utente....")

    user = context.job.chat_data['user']

    print(user)

    # print(context)
    # print(context.chat_data) # None

    chat_id = context.job.chat_data['chat_id']
    print(chat_id)

    # job = context.job

    # print(job)
    # print(job.context) # uguale a chat_id
    # print(job.special_message)

    context.bot.send_document(chat_id=chat_id, document=open('ultima_newsletter.pdf', 'rb'))
    # context.bot.send_message(job.context, text='Beep!')


def mandami_ultima_newsletter(update, context):
    # update.message.reply_text('ok! ti sto mandando l\'ultima newletter disponibile...')

    chat_id = update.message.chat_id

    due = 60

    # Add job to queue
    job2 = context.job_queue.run_once(alarm, due, context=chat_id)
    job2.special_message = 123
    job2.chat_data = {}

    job2.chat_data['chat_id'] = chat_id
    job2.chat_data['user'] = update.message.from_user

    # context.chat_data['job2'] = job2
    # context.chat_data['chat_id'] = chat_id

    job = context.job
    # context.bot.send_message(job.context, text='Beep!')

    # https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets#post-a-file-from-disk
    # context.bot.send_document(chat_id=chat_id, document=open('d:/tmp/me.png', 'rb'))
    context.bot.send_message(chat_id=chat_id, text='tra 60 secondi ti mando la newsletter')


def voglio_ricevere_newsletter(update, context):
    # update.message.reply_text('ok! ti manderò la newsletter')
    chat_id = update.message.chat_id

    context.bot.send_message(chat_id=chat_id,
                             text='ok! ti manderò la newsletter. Intanto ti mando un link <b>bold</b> <i>italic</i> <a href="http://google.com">link</a>.',
                             parse_mode=telegram.ParseMode.HTML)


def basta_newsletter(update, context):
    update.message.reply_text('ok, non ti mando più la newsletter')


# def parole_chiave_newsletter(update, context):
#     chat_id = update.message.chat_id
#
#     location_keyboard = telegram.KeyboardButton(text="send_location", request_location=True)
#     contact_keyboard = telegram.KeyboardButton(text="send_contact", request_contact=True)
#     custom_keyboard = [[location_keyboard, contact_keyboard]]
#     reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
#     context.bot.send_message(chat_id=chat_id,
#                              text="Would you mind sharing your location and contact with me?",
#                              reply_markup=reply_markup)
#
#     update.message.reply_text('ok! ')


# Comando SCEGLI
def scegli_categorie(update, context):

    # print(update)

    django_user = orm_add_user(update.message.from_user)
    print(django_user)

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Seleziona le categorie:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard(django_user))
    )


# def mix(index, django_user):
#     return str(index) + "|" + str(django_user.user_id)
#
# def demix(str):
#     index = str.split("|")
#     a = (index[0])
#     b = int(index[1])
#     return a, b


def inline_keyboard(django_user):
    """ Costruisce la inline_keyboard in base alle categorie già scelte """

    out = []
    # label = ''

    # print("inline_keyboard - keywords selected by current user " + str(django_user.user_id))
    # for item in django_user.keywords.all():
    #     print(item.key + " " + orm_get_default_keywords_dict()[item.key])
    # print("***")

    # Permette di visualizzare nella inline_keyboard le categorie già selezionate

    for index in category.keys():
        key = category[index][1]
        # print(key)

        # print(django_user.keywords.filter(key=index))

        queryset = django_user.keywords.filter(key=index)

        # print("filter for " + index + ", len=" + str(len(queryset)))

        if len(queryset) != 0:
            label = index + ' ->' + str(category[index][0]).upper() + '<-'
        else:
            label = index + " " + str(category[index][0])

        out.append(
                   [InlineKeyboardButton(text=label, callback_data=index)]
                   )

    # Inserisce i pulsanti 'Conferma' e 'Esci'
    out.append(
               [
                   InlineKeyboardButton(text='Chiudi', callback_data='OK'), # OK , 'Conferma'
                   # InlineKeyboardButton(text='Esci', callback_data='ESC') #ESC
               ]
               )

    return out


def choice(update, context):
    print("choice:")
    print(update.callback_query.data)
    print(update)

    # {
    #     'update_id': 715880587,
    #     'callback_query': {
    #         'id': '3798474624479937048',
    #         'chat_instance': '-5186621929499105072',
    #         'message': {
    #             'message_id': 576,
    #             'date': 1567527926,
    #             'chat': {
    #                 'id': 884401291,
    #                 'type': 'private',
    #                 'first_name': 'Marco',
    #                 'last_name': 'Tessarotto',
    #             },
    #             'text': 'Seleziona le categorie:',
    #             'entities': [],
    #             'caption_entities': [],
    #             'photo': [],
    #             'new_chat_members': [],
    #             'new_chat_photo': [],
    #             'delete_chat_photo': False,
    #             'group_chat_created': False,
    #             'supergroup_chat_created': False,
    #             'channel_chat_created': False,
    #             'reply_markup': {'inline_keyboard': [[{'text': 'Lavoro',
    #                                                    'callback_data': '01|884401291'}],
    #                                                  [{'text': 'Chiudi',
    #                                                    'callback_data': '-1|884401291'}]]},
    #             'from': {
    #                 'id': 815938668,
    #                 'first_name': "Marco's test bot",
    #                 'is_bot': True,
    #                 'username': 'marcotts_bot',
    #             },
    #         },
    #         'data': '-1|884401291',
    #         'from': {
    #             'id': 884401291,
    #             'first_name': 'Marco',
    #             'is_bot': False,
    #             'last_name': 'Tessarotto',
    #             'language_code': 'en',
    #         },
    #     },
    #     '_effective_user': {
    #         'id': 884401291,
    #         'first_name': 'Marco',
    #         'is_bot': False,
    #         'last_name': 'Tessarotto',
    #         'language_code': 'en',
    #     },
    #     '_effective_chat': {
    #         'id': 884401291,
    #         'type': 'private',
    #         'first_name': 'Marco',
    #         'last_name': 'Tessarotto',
    #     },
    #     '_effective_message': {
    #         'message_id': 576,
    #         'date': 1567527926,
    #         'chat': {
    #             'id': 884401291,
    #             'type': 'private',
    #             'first_name': 'Marco',
    #             'last_name': 'Tessarotto',
    #         },
    #         'text': 'Seleziona le categorie:',
    #         'entities': [],
    #         'caption_entities': [],
    #         'photo': [],
    #         'new_chat_members': [],
    #         'new_chat_photo': [],
    #         'delete_chat_photo': False,
    #         'group_chat_created': False,
    #         'supergroup_chat_created': False,
    #         'channel_chat_created': False,
    #         'reply_markup': {'inline_keyboard': [[{'text': 'Lavoro',
    #                                                'callback_data': '01|884401291'}],
    #                                              [{'text': '->Studi e ricerche mondo giovani<-'
    #                                                   , 'callback_data': '10|884401291'}],
    #                                              [{'text': '->Garanzia giovani<-',
    #                                                'callback_data': '11|884401291'}],
    #                                              [{'text': 'Chiudi',
    #                                                'callback_data': '-1|884401291'}]]},
    #         'from': {
    #             'id': 815938668,
    #             'first_name': "Marco's test bot",
    #             'is_bot': True,
    #             'username': 'marcotts_bot',
    #         },
    #     },
    # }

    # {
    #     'update_id': 715880584,
    #     'message': {
    #         'message_id': 573,
    #         'date': 1567527704,
    #         'chat': {
    #             'id': 884401291,
    #             'type': 'private',
    #             'first_name': 'Marco',
    #             'last_name': 'Tessarotto',
    #         },
    #         'text': '/scegli_categorie',
    #         'entities': [{'type': 'bot_command', 'offset': 0,
    #                       'length': 17}],
    #         'caption_entities': [],
    #         'photo': [],
    #         'new_chat_members': [],
    #         'new_chat_photo': [],
    #         'delete_chat_photo': False,
    #         'group_chat_created': False,
    #         'supergroup_chat_created': False,
    #         'channel_chat_created': False,
    #         'from': {
    #             'id': 884401291,
    #             'first_name': 'Marco',
    #             'is_bot': False,
    #             'last_name': 'Tessarotto',
    #             'language_code': 'en',
    #         },
    #     },
    #     '_effective_user': {
    #         'id': 884401291,
    #         'first_name': 'Marco',
    #         'is_bot': False,
    #         'last_name': 'Tessarotto',
    #         'language_code': 'en',
    #     },
    #     '_effective_chat': {
    #         'id': 884401291,
    #         'type': 'private',
    #         'first_name': 'Marco',
    #         'last_name': 'Tessarotto',
    #     },
    #     '_effective_message': {
    #         'message_id': 573,
    #         'date': 1567527704,
    #         'chat': {
    #             'id': 884401291,
    #             'type': 'private',
    #             'first_name': 'Marco',
    #             'last_name': 'Tessarotto',
    #         },
    #         'text': '/scegli_categorie',
    #         'entities': [{'type': 'bot_command', 'offset': 0,
    #                       'length': 17}],
    #         'caption_entities': [],
    #         'photo': [],
    #         'new_chat_members': [],
    #         'new_chat_photo': [],
    #         'delete_chat_photo': False,
    #         'group_chat_created': False,
    #         'supergroup_chat_created': False,
    #         'channel_chat_created': False,
    #         'from': {
    #             'id': 884401291,
    #             'first_name': 'Marco',
    #             'is_bot': False,
    #             'last_name': 'Tessarotto',
    #             'language_code': 'en',
    #         },
    #     },
    # }

    django_user = orm_add_user(update.callback_query.from_user)


    # scelta, user_id = demix(update.callback_query.data)

    scelta = update.callback_query.data

    # print("scelta = " + str(scelta))

    #django_user = orm_get_user(user_id)

    if scelta == 'OK':  # 'OK'  Stampa le categorie scelte
        cat_scelte = ''
        for index in category.keys():
            if category[index][1]:
                cat_scelte += ' - ' + category[index][0] + '  ' + category[index][2] + '\n'

        for index in category.keys():
            key = category[index][1]
            # print(key)

            # print(django_user.keywords.filter(key=index))

            if len(django_user.keywords.filter(key=index)) != 0:
                cat_scelte += ' - ' + category[index][0] + '  ' + category[index][2] + '\n'



        # Nel caso in cui non sia stata scelta alcuna categoria viene inviato un
        # messaggio di allerta
        if cat_scelte == '':
            update.callback_query.answer(
                text='Non è stata scelta alcuna categoria!',
                show_alert=True
            )
            return

        update.callback_query.edit_message_text(
            text='Hai scelto:\n\n' + cat_scelte +
                 '\nDigita /scegli_categorie per modificare'
        )

    elif scelta == 'ESC':  # 'ESC' Reimposta i valori di category
        for index in category.keys():
            category[index][1] = False

        update.callback_query.edit_message_text(
            text='Scelta annullata;\n'
                 'digita /scegli_categorie per ricominciare'
        )

    else:  # Toggle checked/unchecked per la categoria selezionata

        update_user_keyword_settings(django_user, scelta)


        # category[scelta][1] = ~category[scelta][1]

        update.callback_query.edit_message_text(
            text="Seleziona le categorie:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard(django_user))
        )


REQUEST_KWARGS = {
    # 'proxy_url': 'http://localhost:3128/',
    # Optional, if you need authentication:
    # 'username': 'PROXY_USER',
    # 'password': 'PROXY_PASS',
}

import os

token = os.environ.get('TOKEN') or open('token.txt').read().strip()

updater = Updater(token=token, use_context=True, request_kwargs=REQUEST_KWARGS)

updater.dispatcher.add_handler(CommandHandler('hello', hello))

updater.dispatcher.add_handler(CommandHandler('start', start))

updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('aiuto', help))

updater.dispatcher.add_handler(CommandHandler('mandami_ultima_newsletter', mandami_ultima_newsletter))
updater.dispatcher.add_handler(CommandHandler('voglio_ricevere_newsletter', voglio_ricevere_newsletter))
#updater.dispatcher.add_handler(CommandHandler('basta_newsletter', basta_newsletter))
#updater.dispatcher.add_handler(CommandHandler('parole_chiave_newsletter', parole_chiave_newsletter))

updater.dispatcher.add_handler(CommandHandler('condividi_posizione', condividi_posizione))

updater.dispatcher.add_handler(CommandHandler('scegli_categorie', scegli_categorie))

updater.dispatcher.add_handler(CallbackQueryHandler(choice))

updater.start_polling()
updater.idle()
