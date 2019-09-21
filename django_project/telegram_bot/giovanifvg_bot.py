import os

# cd Scrivania/progetto_tesi
# export PYTHONPATH=.:django_project/telegram_bot
# python django_project/telegram_bot/giovanifvg_bot.py

from django_project.telegram_bot.ormlayer import *

from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters
)

from django_project.telegram_bot.choose_categories import (
    choose,
    callback_choice
)
from django_project.telegram_bot.send_news import (
    news,
    comment,
    callback_comment,
    callback_feedback
)

import logging

# Spiega quando (e perché) le cose non funzionano come ci si aspetta
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


help_msg = 'Ecco i comandi a disposizione:\n' \
           '\n' \
           '<b>/scegli</b> - permette di impostare le categorie che ti interessano\n' \
           '<b>/invia_articoli</b> - invia l\'articolo di prova\n' \
           '<b>/start</b> - avvia il servizio\n' \
           '<b>/gestisci_commenti</b> - permette di modificare o eliminare i commenti\n' \
           '\n' \
           'Per mostrare nuovamente questo messaggio digita /help, oppure /aiuto.'


# ****************************************************************************************
def start(update, context):
    """ Registra l'utente, nel caso sia al primo accesso; mostra i comandi disponibili """

    print(context.args)  # parametro via start; max 64 caratteri
    # https://telegram.me/marcotts_bot?start=12345

    print(update.message.from_user)
    django_user = orm_add_user(update.message.from_user)
    print("result from orm_add_user: " + str(django_user))

    update.message.reply_text(
        'Ciao ' + update.message.from_user.first_name + '! '
        'Benvenuto al bot Telegram di GiovaniFVG :)'
    )

    update.message.reply_text(
        help_msg,
        parse_mode='HTML'
    )


def help(update, context):
    """ Mostra i comandi disponibili """

    update.message.reply_text(
        help_msg,
        parse_mode='HTML'
    )
    print(context.user_data)


def callback(update, context):
    """ Gestisce i callback_data inviati dalle inline_keyboard """

    data = update.callback_query.data.split()

    if data[0] == 'feedback':
        callback_feedback(update, data[1:])

    elif data[0] == 'comment':
        callback_comment(update, context, data[1])

    elif data[0] == 'choose':
        callback_choice(update, data[1])


# ****************************************************************************************
def main():
    token = os.environ.get('TOKEN') or open('token.txt').read().strip()

    updater = Updater(token=token, use_context=True)
    dp = updater.dispatcher

    # Aggiunta dei vari handler
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))

    # Handlers da .send_news.py
    dp.add_handler(CommandHandler('invia_articoli', news))
    dp.add_handler(MessageHandler(Filters.reply, comment))

    # Handlers da .choose_categories.py
    dp.add_handler(CommandHandler('scegli', choose))

    # handler per servire TUTTE le inline_keyboard
    dp.add_handler(CallbackQueryHandler(callback))

    # Avvio l'updater
    updater.start_polling()

    # Arresta il bot in caso sia stato premuto Ctrl+C o il processo abbia ricevuto SIGINT, SIGTERM o SIGABRT
    updater.idle()


if __name__=='__main__':
    main()
