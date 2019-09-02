import time
import datetime

import telegram
from telegram.ext import Updater, CommandHandler

from ormlayer import orm_add_user


from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup
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

# Dizionario contenente le categorie tra cui scegliere
# Colonna 1 -> Nome categoria
# Colonna 2 -> Checked/Unchecked
# Colonna 3 -> Emoji
category = {
    '01': ['Lavoro', False,  u'\U0001F4BC'],
    '02': ['Studio e formazione', False, u'\U0001F4DA'],
	  '03': ['Mobilità all’estero', False, u'\U00002708'],
	  '04': ['Associazionismo e partecipazione', False, u'\U0001F46B\U0001F46B'],
	  '05': ['Casa e servizi alla persona', False, u'\U0001F4DA'],
	  '06': ['Eventi e tempo libero', False, u'\U0001F4DA'],
	  '07': ['Star bene', False, u'\U0001F4DA'],
	  '08': ['Giovani eccellenze in FVG', False, u'\U0001F4DA'],
	  '09': ['La regione FVG per i giovani', False, u'\U0001F4DA'],
	  '10': ['Studi e ricerche mondo giovani', False, u'\U0001F4DA'],
	  '11': ['Garanzia giovani', False, u'\U0001F4DA']
}


#pip install python-telegram-bot==12.0.0b1 --upgrade


comandi_disponibili = "/start\n" \
                      "/mandami_ultima_newsletter\n" \
                      "/voglio_ricevere_newsletter\n" \
                      "/basta_newsletter\n" \
                      "/parole_chiave_newsletter\n" \
                      "/condividi_posizione\n" \
                      "/scegli"
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

    print(context.args) # parametro via start; max 64 caratteri
    # https://telegram.me/marcotts_bot?start=12345

    print(update.message.from_user)
    orm_add_user(update.message.from_user)

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


# Comando SCEGLI
def scegli(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Seleziona una o più categorie tra le seguenti",
        reply_markup=InlineKeyboardMarkup(inline_keyboard())
    )


def inline_keyboard():
    """ Costruisce la inline_keyboard in base alle categorie già scelte """

    out = []
    label = ''

    # Permette di visualizzare nella inline_keyboard le categorie già selezionate
    for index in category.keys():
        if category[index][1]:
            label = '-> ' + str(category[index][0]) + ' <-'
        else:
            label = str(category[index][0])

        out.insert(0,
                   [InlineKeyboardButton(text=label, callback_data=index)]
                   )

    # Inserisce i pulsanti 'Conferma' e 'Esci'
    out.insert(0,
               [
                   InlineKeyboardButton(text='Conferma', callback_data='OK'),
                   InlineKeyboardButton(text='Esci', callback_data='ESC')
               ]
               )

    return reversed(out)


def choice(update, context):

    print(update.callback_query.data)

    scelta = str(update.callback_query.data)

    if scelta == 'OK':  # Stampa le categorie scelte
        cat_scelte = ''
        for index in category.keys():
            if category[index][1]:
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
                 '\nDigita /scegli per modificare'
        )

    elif scelta == 'ESC':  # Reimposta i valori di category
        for index in category.keys():
            category[index][1] = False

        update.callback_query.edit_message_text(
            text='Scelta annullata;\n'
                 'digita /scegli per ricominciare'
        )

    else:  # Toggle checked/unchecked per la categoria selezionata
        category[scelta][1] = ~category[scelta][1]

        update.callback_query.edit_message_text(
            text="Seleziona la categoria:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard())
        )


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

updater.dispatcher.add_handler( CommandHandler('scegli', scegli) )

updater.dispatcher.add_handler( CallbackQueryHandler(choice) )


updater.start_polling()
updater.idle()
