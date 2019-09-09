import time
import datetime

import telegram

# cd /home/marco/Documents/github/giovanifvg-bot
# export PYTHONPATH=/home/marco/Documents/github/giovanifvg-bot/:/home/marco/Documents/github/giovanifvg-bot/gfvgbo/telegrambot/
# python /home/marco/Documents/github/giovanifvg-bot/gfvgbo/telegrambot/telegrambot.py

# cd Scrivania/m_test_bbot/giovanifvg-bot/
# export PYTHONPATH=.:gfvgbo/telegrambot
# python gfvgbo/telegrambot/telegrambot.py

from gfvgbo.telegrambot.ormlayer import (
    orm_add_user,
    update_user_keyword_settings,
    orm_get_user,
    orm_get_default_keywords_dict
)

from gfvgbo.backoffice.definitions import get_categories_dict
category = get_categories_dict()

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    Filters
)

import logging

# Spiega quando (e perché) le cose non funzionano come ci si aspetta
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# pip install python-telegram-bot==12.0.0 --upgrade

comandi_disponibili = "/help oppure /aiuto\n" \
                      "/start\n" \
                      "/invia_news\n" \
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


def news(update, context):

    folder_new = 'demo_new'    
    
    fd = open(folder_new + '/category', 'r')
    cat = fd.read()[:-1]
    fd.close()
        
    fd = open(folder_new + '/title', 'r')
    title = fd.read()
    fd.close()
    
    fd = open(folder_new + '/body', 'r')
    body = fd.read()
    fd.close()
    
    fd = open(folder_new + '/link', 'r')
    link = fd.read()
    fd.close()
    
    # Costruzione della descrizione
    text = '<b>' + str(title) + '</b>'
        
    body = body.split()
    text += str(" ".join(body[0:30]))
    
    # Aggiunta del link per approfondire
    text += '... <a href=\"' + link + '\">continua</a>'

    context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=open(folder_new + '/allegato_1.jpg', 'rb'),
            caption=text,
            parse_mode='HTML'
    )
    
    # Attivazione tastiera con pulsanti 'like' e 'dislike'
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Ti è piaciuto l'articolo?",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(text=u'\u2717', callback_data='dislike'),
                InlineKeyboardButton(text=u'\u2713', callback_data='like')
            ]
        ])
    )
    
    return REACT


# Gestore dei feedback sulle news
def reaction(update, context):

    print(update)

    sel = update.callback_query.data    
    
    if sel=='like': print('LIKE')
    else: print('DISLIKE')
    
    update.callback_query.edit_message_text(
            'Grazie per il feedback!\n'
            'Puoi commentare la notizia scrivendo\n'
            '\"Commento: \" <i>il tuo commento</i>',
            parse_mode='HTML'
    )
        
    return COMMENT


# Gestore dei commenti alle news
def comment(update, context):
    
    text = update.message.text
    
    #if not re.match('Commento:.*', text):
    #    context.bot.answer(
    #            text='Il commento inserito non è valido'
    #    )
    
    print(text[10:])
    
    return ConversationHandler.END
    


def voglio_ricevere_newsletter(update, context):

    context.bot.send_message(
            chat_id=update.message.chat_id,
            text='ok! ti manderò la newsletter. Intanto ti mando un link <a href="http://google.com">link</a>.',
            parse_mode=telegram.ParseMode.HTML
    )


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


# Comando SCEGLI_CATEGORIE
def scegli_categorie(update, context):

    django_user = orm_add_user(update.message.from_user)
    print('\n' + str(django_user))

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Seleziona una o più categorie:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard(django_user))
    )
    
    return CHOOSE

# def mix(index, django_user):
#     return str(index) + "|" + str(django_user.user_id)
#
# def demix(str):
#     index = str.split("|")
#     a = (index[0])
#     b = int(index[1])
#     return a, b

# Viene passato al seguente metodo il parametro identificativo dell'utente connesso
def inline_keyboard(django_user):
    """ Costruisce la inline_keyboard in base alle categorie già scelte """

    result = []

    # print("inline_keyboard - keywords selected by current user " + str(django_user.user_id))
    # for item in django_user.keywords.all():
    #     print(item.key + " " + orm_get_default_keywords_dict()[item.key])
    # print("***")
    
    # Permette di visualizzare nella inline_keyboard le categorie già selezionate
    for index in category.keys():

        queryset = django_user.keywords.filter(key=index)

        label = str(category[index][0])
        if len(queryset) != 0:
            label = u' \u2737  ' + label.upper() + u' \u2737'
           
        result.append( [InlineKeyboardButton(text=label, callback_data=index)] )

        # print("filter for " + index + ", len=" + str(len(queryset)))

    # Inserisce il pulsante 'CHIUDI'
    result.append( [InlineKeyboardButton(text='CHIUDI', callback_data='OK')] )

    return result


def choice(update, context):
    print("\nchoice:", update.callback_query.data)
    print(update)

    django_user = orm_add_user(update.callback_query.from_user)

    # scelta, user_id = demix(update.callback_query.data)

    scelta = update.callback_query.data

    if scelta == 'OK':  # 'OK'  Stampa le categorie scelte
        cat_scelte = ''
        for index in category.keys():

            queryset = django_user.keywords.filter(key=index)

            if len(queryset) != 0:
                cat_scelte += '- ' + category[index][0] + '  ' + category[index][1] + '\n'

        # ALERT: Non è stata scelta alcuna categoria!
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
        
        return ConversationHandler.END

    else:  # Toggle checked/unchecked per la categoria selezionata
        update_user_keyword_settings(django_user, scelta)


        update.callback_query.edit_message_text(
            text="Seleziona una o più categorie:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard(django_user))
        )
        
        return CHOOSE


REQUEST_KWARGS = {
    # 'proxy_url': 'http://localhost:3128/',
    # Optional, if you need authentication:
    # 'username': 'PROXY_USER',
    # 'password': 'PROXY_PASS',
}

import os
token = os.environ.get('TOKEN') or open('token.txt').read().strip()

updater = Updater(token=token, use_context=True, request_kwargs=REQUEST_KWARGS)
dp = updater.dispatcher

# Aggiunta dei vari handler
dp.add_handler(CommandHandler('hello', hello))

dp.add_handler(CommandHandler('start', start))

dp.add_handler(CommandHandler('help', help))
dp.add_handler(CommandHandler('aiuto', help))

# ConversationHandler per l'invio delle news
REACT, COMMENT = range(2)
send_news = ConversationHandler(
    entry_points=[ CommandHandler('invia_news', news) ],
    states={
            REACT: [ CallbackQueryHandler(reaction) ],
            COMMENT: [ MessageHandler(Filters.text, comment) ]
    },
    fallbacks=[],    
    allow_reentry=True
)

dp.add_handler(send_news)

# ConversationHandler per la scelta delle categorie
CHOOSE = range(1)
choose_categories = ConversationHandler(
    entry_points=[ CommandHandler('scegli_categorie', scegli_categorie) ],
    states={
            CHOOSE: [ CallbackQueryHandler(choice) ]
    },
    fallbacks=[],    
    allow_reentry=True
)

dp.add_handler(choose_categories)


dp.add_handler(CommandHandler('voglio_ricevere_newsletter', voglio_ricevere_newsletter))
#dp.add_handler(CommandHandler('basta_newsletter', basta_newsletter))
#dp.add_handler(CommandHandler('parole_chiave_newsletter', parole_chiave_newsletter))

dp.add_handler(CommandHandler('condividi_posizione', condividi_posizione))



# Avvio l'updater
updater.start_polling()
  
# Arresta il bot in caso sia stato premuto Ctrl+C o il processo abbia ricevuto SIGINT, SIGTERM o SIGABRT
updater.idle()
