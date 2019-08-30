import time
import datetime

import telegram
from telegram.ext import Updater, CommandHandler

#pip install python-telegram-bot==12.0.0b1 --upgrade


comandi_disponibili = "/start\n" \
                      "/mandami_ultima_newsletter\n" \
                      "/voglio_ricevere_newsletter\n" \
                      "/basta_newsletter\n" \
                      "/parole_chiave_newsletter\n" \
                      "/condividi_posizione\n"
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
    update.message.reply_text(
        'Ciao {}, benvenuto al servizio GiovaniFVG,\nhai a disposizione i seguenti comandi:\n'.format(update.message.from_user.first_name) + comandi_disponibili)


def help(update, context):
    update.message.reply_text('comandi:\n' + comandi_disponibili)


def alarm(context):
    """Send the alarm message."""
    print_timestamp()
    print("ora manderò una newsletter all'utente....")

    user = context.job.chat_data['user']

    print(user)

    #print(context)
    #print(context.chat_data) # None

    chat_id = context.job.chat_data['chat_id']
    print(chat_id)

    #job = context.job

    #print(job)
    #print(job.context) # uguale a chat_id
    #print(job.special_message)


    context.bot.send_document(chat_id=chat_id, document=open('ultima_newsletter.pdf', 'rb'))
    #context.bot.send_message(job.context, text='Beep!')


def mandami_ultima_newsletter(update, context):
    #update.message.reply_text('ok! ti sto mandando l\'ultima newletter disponibile...')

    chat_id = update.message.chat_id

    due=60

    # Add job to queue
    job2 = context.job_queue.run_once(alarm, due, context=chat_id)
    job2.special_message = 123
    job2.chat_data = {}

    job2.chat_data['chat_id'] = chat_id
    job2.chat_data['user'] = update.message.from_user

    #context.chat_data['job2'] = job2
    #context.chat_data['chat_id'] = chat_id


    job = context.job
    #context.bot.send_message(job.context, text='Beep!')

    # https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets#post-a-file-from-disk
    #context.bot.send_document(chat_id=chat_id, document=open('d:/tmp/me.png', 'rb'))
    context.bot.send_message(chat_id=chat_id, text='tra 60 secondi ti mando la newsletter')


def voglio_ricevere_newsletter(update, context):
    #update.message.reply_text('ok! ti manderò la newsletter')
    chat_id = update.message.chat_id

    context.bot.send_message(chat_id=chat_id,
                     text='ok! ti manderò la newsletter. Intanto ti mando un link <b>bold</b> <i>italic</i> <a href="http://google.com">link</a>.',
                     parse_mode=telegram.ParseMode.HTML)


def basta_newsletter(update, context):
    update.message.reply_text('ok, non ti mando più la newsletter')


def parole_chiave_newsletter(update, context):
    chat_id = update.message.chat_id

    location_keyboard = telegram.KeyboardButton(text="send_location", request_location=True)
    contact_keyboard = telegram.KeyboardButton(text="send_contact", request_contact=True)
    custom_keyboard = [[location_keyboard, contact_keyboard]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    context.bot.send_message(chat_id=chat_id,
                             text="Would you mind sharing your location and contact with me?",
                             reply_markup=reply_markup)


    update.message.reply_text('ok! ')


REQUEST_KWARGS={
    #'proxy_url': 'http://localhost:3128/',
    # Optional, if you need authentication:
    #'username': 'PROXY_USER',
    #'password': 'PROXY_PASS',
}
import os
token = os.environ.get('TOKEN') or open('token.txt').read().strip()

updater = Updater(token=token, use_context=True, request_kwargs=REQUEST_KWARGS)

updater.dispatcher.add_handler(CommandHandler('hello', hello))

updater.dispatcher.add_handler(CommandHandler('start', start))


updater.dispatcher.add_handler(CommandHandler('help', help))

updater.dispatcher.add_handler(CommandHandler('mandami_ultima_newsletter', mandami_ultima_newsletter))
updater.dispatcher.add_handler(CommandHandler('voglio_ricevere_newsletter', voglio_ricevere_newsletter))
updater.dispatcher.add_handler(CommandHandler('basta_newsletter', basta_newsletter))
updater.dispatcher.add_handler(CommandHandler('parole_chiave_newsletter', parole_chiave_newsletter))


updater.dispatcher.add_handler(CommandHandler('condividi_posizione', condividi_posizione))


updater.start_polling()
updater.idle()
