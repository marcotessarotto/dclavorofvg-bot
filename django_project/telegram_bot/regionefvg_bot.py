import os

# cd Scrivania/regionefvg_bot
# export PYTHONPATH=.:django_project/telegram_bot
# python django_project/telegram_bot/regionefvg_bot.py

from django_project.telegram_bot.ormlayer import *

from telegram.ext import *
from telegram import *

import logging

# Spiega quando (e perché) le cose non funzionano come ci si aspetta
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Messaggio da mostrare quando viene chiamato /help
help_msg = 'Ecco i comandi a disposizione:\n' \
           '\n' \
           '<b>/scegli</b> permette di impostare le categorie che ti interessano\n' \
           '<b>/invia_articoli</b> invia l\'articolo di prova\n' \
           '<b>/start</b> avvia il servizio\n' \
           '<b>/privacy</b> gestisci la privacy\n' \
           '\n' \
           'Per avviare un comando digitalo da tastiera oppure selezionalo da questa lista.\n' \
           'Per mostrare nuovamente questo messaggio digita /help, oppure /aiuto.'


# ****************************************************************************************
def start(update, context):
    """ Registra l'utente, nel caso sia al primo accesso; mostra i comandi disponibili """

    print(context.args)  # parametro via start; max 64 caratteri
    # https://telegram.me/marcotts_bot?start=12345

    orm_add_user(update.message.from_user)

    update.message.reply_text(
        'Ciao ' + update.message.from_user.first_name + '! '
                                                        'Benvenuto al bot Telegram di RegioneFVG :)'
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


def privacy(update, context):
    user = orm_get_user(update.message.from_user.id)

    privacy_state = user.has_accepted_privacy_rules

    print("privacy - user = " + str(user) + " " + str(privacy_state))

    if not privacy_state:
        #

        buttons = [[InlineKeyboardButton(text='ACCETTO', callback_data='privacy ACCETTO'),
                    InlineKeyboardButton(text='NON ACCETTO', callback_data='privacy NON_ACCETTO')]
                   ]

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Accetti la privacy? (.....)",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

        return

    update.message.reply_text(
        'hai accettato la privacy: ' + str(user.has_accepted_privacy_rules),
        parse_mode='HTML'
    )


def callback_privacy(update, context, param):
    id_utente = update.callback_query.from_user.id

    # print("callback_privacy - id_utente = " + str(id_utente))

    update.callback_query.edit_message_text(text="ok impostazione privacy = " + param)

    if param == "ACCETTO":
        privacy_setting = True
    else:
        privacy_setting = False

    orm_change_user_privacy_setting(id_utente, privacy_setting)


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
from django_project.backoffice.definitions import get_categories_dict

category = get_categories_dict()  # Importa e memorizza il dict delle categorie di default


def choose(update, context):
    """ Permette all'utente di scegliere tra le categorie disponibili """

    user = orm_get_user(update.message.from_user.id)

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Seleziona una o più categorie:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard(user))
    )


def inline_keyboard(user):
    """ Costruisce la inline_keyboard in base alle categorie già scelte
    dall'utente passato per parametro """

    keyboard = []

    for index in category.keys():

        queryset = user.categories.filter(key=index)

        label = str(category[index][0]) + ' ' + category[index][1]
        if len(queryset) != 0:
            label = u'\U00002705' + ' ' + label.upper()
        else:
            label = u'\U0000274C' + ' ' + label

        keyboard.append([InlineKeyboardButton(
            text=label,
            callback_data='choice ' + index)]
        )

    # Inserisce il pulsante 'CHIUDI'
    keyboard.append(
        [InlineKeyboardButton(text='CHIUDI', callback_data='choice OK')]
    )

    return keyboard


def callback_choice(update, scelta):
    """ Gestisce i pulsanti premuti nella inline_keyboard """

    user = orm_get_user(update.callback_query.from_user.id)

    if scelta == 'OK':  # 'OK'  Stampa le categorie scelte
        cat_scelte = ''
        for index in category.keys():
            queryset = user.categories.filter(key=index)

            if len(queryset) != 0:
                cat_scelte += '- ' + category[index][0] + \
                              '  ' + category[index][1] + '\n'

        # ALERT: Non è stata scelta alcuna categoria!
        if cat_scelte == '':
            update.callback_query.answer(
                text='Non è stata scelta alcuna categoria!',
                show_alert=True
            )
            return

        update.callback_query.edit_message_text(
            text='Ok, le categorie sono state impostate con successo. '
                 'Hai scelto:\n\n' + cat_scelte +
                 '\nDigita /scegli per modificare.'
        )

    else:  # Toggle checked/unchecked per la categoria selezionata
        update_user_category_settings(user, scelta)

        update.callback_query.edit_message_text(
            text="Seleziona una o più categorie:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard(user))
        )


# SEZIONE INVIO NEWS
# ****************************************************************************************
def news(update, context):
    """ Invia un nuovo articolo """

    folder_new = '/home/marco/Documents/github/dclavorofvg-bot/demo_new'

    # fd = open(folder_new + '/category', 'r')
    # cat = fd.read()[:-1]

    fd = open(folder_new + '/title', 'r')
    title = fd.read()[:-1]

    fd = open(folder_new + '/body', 'r')
    body = fd.read()

    fd = open(folder_new + '/link', 'r')
    link = fd.read()
    fd.close()

    news_item = orm_add_newsitem(title, body, link)
    context.user_data['news_id'] = news_item.news_id

    # Costruzione della descrizione
    caption = '<b>' + str(news_item.title) + \
              ' [' + news_item.news_id + ']</b>\n'

    text = news_item.text.split()
    caption += str(" ".join(text[:30]))

    # Aggiunta del link per approfondire
    caption += '... <a href=\"' + news_item.link + '\">continua</a>'

    context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo=open(folder_new + '/allegato_1.jpg', 'rb'),
        caption=caption,
        parse_mode='HTML'
    )

    # Attivazione tastiera con pulsanti 'like' e 'dislike'
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Ti è piaciuto l'articolo?",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(  # Pulsante dislike
                text=u'\u2717',
                callback_data='feedback - ' + news_item.news_id
            ),
            InlineKeyboardButton(  # Pulsante like
                text=u'\u2713',
                callback_data='feedback + ' + news_item.news_id
            )
        ]])
    )


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


def comment(update, context):
    """ Memorizza il commento inserito dall'utente """

    # Testo del messaggio cui il commento fornisce una risposta
    # (c'è il codice dell'articolo)
    reply_data = update.message.reply_to_message.text.split()
    orm_add_comment(update.message.text, reply_data[2], update.message.from_user.id)

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Commento caricato con successo!'
    )


# ****************************************************************************************
def main():
    from pathlib import Path
    token_file = Path('token.txt')

    if not token_file.exists():
        token_file = Path('../../token.txt')

    token = os.environ.get('TOKEN') or open(token_file).read().strip()

    updater = Updater(token=token, use_context=True)
    dp = updater.dispatcher

    # Aggiunta dei vari handler
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('aiuto', help))
    dp.add_handler(CommandHandler('privacy', privacy))

    # Handlers per la sezione INVIO NEWS
    dp.add_handler(CommandHandler('invia_articoli', news))
    dp.add_handler(MessageHandler(Filters.reply, comment))

    # Handlers per la sezione SCELTA CATEGORIE
    dp.add_handler(CommandHandler('scegli', choose))

    # Handler per servire TUTTE le inline_keyboard
    dp.add_handler(CallbackQueryHandler(callback))

    # Avvio l'updater
    updater.start_polling()

    # Arresta il bot in caso sia stato premuto Ctrl+C o il processo abbia ricevuto SIGINT, SIGTERM o SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
