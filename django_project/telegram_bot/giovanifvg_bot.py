import os

# cd Scrivania/progetto_tesi
# export PYTHONPATH=.:django_project/telegram_bot
# python django_project/telegram_bot/giovanifvg_bot.py

from django_project.telegram_bot.ormlayer import *

from telegram.ext import *
from telegram import *

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


# SEZIONE SCELTA CATEGORIE
# ****************************************************************************************
from django_project.backoffice.definitions import get_categories_dict
category = get_categories_dict()


def choose(update, context):
    """ Permette all'utente di scegliere tra le categorie disponibili """

    user = orm_add_user(update.message.from_user)

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Seleziona una o più categorie:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard(user))
    )


def inline_keyboard(user):
    """ Costruisce la inline_keyboard in base alle categorie già scelte """

    result = []

    for index in category.keys():

        queryset = user.categories.filter(key=index)

        label = str(category[index][0])
        if len(queryset) != 0:
            label = u' \u2737  ' + label.upper() + u' \u2737'

        result.append([InlineKeyboardButton(
            text=label,
            callback_data='choose ' + index)]
        )

    # Inserisce il pulsante 'CHIUDI'
    result.append(
        [InlineKeyboardButton(text='CHIUDI', callback_data='choose OK')]
    )

    return result


def callback_choice(update, scelta):
    user = orm_add_user(update.callback_query.from_user)

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

    folder_new = 'demo_new'

    fd = open(folder_new + '/category', 'r')
    cat = fd.read()[:-1]

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
                InlineKeyboardButton(
                    text=u'\u2717',
                    callback_data='feedback - ' + news_item.news_id
                ),
                InlineKeyboardButton(
                    text=u'\u2713',
                    callback_data='feedback + ' + news_item.news_id
                )
        ]])
    )


def callback_feedback(update, data):
    """ Gestisce i feedback sugli articoli """

    feed = data[0]
    news_id = data[1]
    orm_add_feedback(feed, news_id)

    update.callback_query.edit_message_text(
        text='Grazie per il feedback!\n',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(
                text='Commenta',
                callback_data='comment ' + news_id)]
        ])
    )


def callback_comment(update, context, news_id):
    """ Gestisce i commenti agli articoli """

    update.callback_query.edit_message_text(
        'Grazie per il feedback!'
    )

    context.bot.send_message(
        chat_id=update.callback_query.message.chat_id,
        text='Commento art. ' + news_id,
        reply_markup=ForceReply()
    )


def comment(update, context):

    reply = update.message.reply_to_message.text.split()
    text = update.message.text
    orm_add_comment(text, reply[2], update.message.from_user.id)

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Commento caricato con successo!'
    )


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
