import os

# cd Scrivania/regionefvg_bot
# export PYTHONPATH=.:django_project/telegram_bot
# python django_project/telegram_bot/regionefvg_bot.py

from django_project.telegram_bot.ormlayer import *

from telegram.ext import *
from telegram import *

import telegram.bot
from telegram.ext import messagequeue as mq

import logging

from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)

# Spiega quando (e perché) le cose non funzionano come ci si aspetta
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Messaggio da mostrare quando viene chiamato /help
help_msg = 'Questi sono i comandi a disposizione:\n' \
           '\n' \
           '<b>/start</b> avvia il bot\n' \
           '<b>/scegli</b> scegli le categorie di notizie che ti interessano\n' \
           '<b>/privacy</b> gestisci la privacy\n' \
           '\n' \
           '<b>***SOLO PER DEBUG***: /invia_articoli</b> invia l\'articolo di prova\n' \
           '\n' \
           'Per avviare un comando digitalo da tastiera oppure selezionalo dalla lista.\n' \
           'Per mostrare nuovamente questo messaggio digita /help o /aiuto o /start'


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

    telegram_user = orm_add_user(update.message.from_user) # orm_add_user always returns a TelegramUser instance

    update.message.reply_text(
        'Ciao ' + update.message.from_user.first_name + '! '
                                                        'Benvenuto al bot Telegram della '
                                                        'Direzione centrale lavoro, formazione, istruzione e famiglia - '
                                                        'Regione Autonoma Friuli Venezia Giulia :)'
    )

    # if check_user_privacy_approval(telegram_user, update, context):
    if not telegram_user.has_accepted_privacy_rules:
        # privacy not yet approved by user
        return privacy(update, context)

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
            help_msg,
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
from django_project.backoffice.definitions import get_categories_dict

category = get_categories_dict()  # Importa e memorizza il dict delle categorie di default


def choose_news_categories(update, context):
    """ Permette all'utente di scegliere tra le categorie disponibili """

    user = orm_get_user(update.message.from_user.id)

    if check_user_privacy_approval(user, update, context):
        # privacy not yet approved by user
        return

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text= orm_get_system_parameter("seleziona le categorie di news"),
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
            text='Grazie, hai scelto le seguenti categorie:\n\n' + cat_scelte +
                 '\nPuoi modificarle in qualsiasi momento usando il comando /scegli .'
        )

    else:  # Toggle checked/unchecked per la categoria selezionata
        update_user_category_settings(user, scelta)

        update.callback_query.edit_message_text(
            text="Seleziona una o più categorie:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard(user))
        )


def news_dispatcher(context: telegram.ext.CallbackContext):
    list_of_news = orm_get_news_to_send()

    if len(list_of_news) == 0:
        print("news_dispatcher - nothing to do")
        return
    else:
        print("news_dispatcher - there are news to process: " + str(len(list_of_news)))

    all_users = orm_get_all_users()

    # TODO

    pass


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


def debug_method(update, context):
    #debug only

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


def callback_minute(context: telegram.ext.CallbackContext):
    all_users = orm_get_all_users()

    for user in all_users:
        print("*** " + str(user.user_id))

        context.bot.send_message(chat_id=user.user_id,
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

    job_minute = job_queue.run_repeating(news_dispatcher, interval=600, first=0) # callback_minute

    # Aggiunta dei vari handler
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('inizia', start))

    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('aiuto', help))
    dp.add_handler(CommandHandler('privacy', privacy))

    dp.add_handler(CommandHandler('fine', detach_from_bot))

    # Handlers per la sezione INVIO NEWS
    dp.add_handler(CommandHandler('invia_articoli', news))  # DEBUG only
    dp.add_handler(MessageHandler(Filters.reply, comment))

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
