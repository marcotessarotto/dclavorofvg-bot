# Dizionario contenente le categorie tra cui scegliere
# Colonna 1 -> Nome categoria
# Colonna 2 -> Checked/Unchecked
# Colonna 3 -> Emoji
# DEFAULT_CATEGORY_DICT = {
#     '01': ['Lavoro', u'\U0001F4BC'],
#     '02': ['Studio e formazione', u'\U0001F4DA'],
#     '03': ['Mobilità all’estero', u'\U00002708'],
#     '04': ['Associazionismo e partecipazione', u'\U0001F465'],
#     '05': ['Casa e servizi alla persona', u'\U0001F3E0'],
#     '06': ['Eventi e tempo libero', u'\U0001F3AD'],
#     '07': ['Star bene', u'\U0001F9D8'],
#     '08': ['Giovani eccellenze in FVG', u'\U0001F393'],
#     '09': ['La regione FVG per i giovani', u'\U0001F91D'],
#     '10': ['Studi e ricerche mondo giovani', u'\U0001F4DD'],
#     '11': ['Garanzia giovani', u'\U0001F3DB'],
#     '12': ['Offerte di lavoro', u'\U0001F3D7'],
#     '13': ['Collocamento mirato', u'\U0001F305'],
# }

DEFAULT_CATEGORY_DICT = {
    '01': ['Lavoro', u'\U0001F4BC', 'lavoro'],
    '02': ['Studio/formazione e corsi', u'\U0001F4DA', 'formazione'],
    '03': ['Mobilità all’estero', u'\U00002708', 'estero'],
    '06': ['Eventi e recruiting', u'\U0001F3AD', 'eventi'],
    '12': ['Offerte di lavoro', u'\U0001F3D7', 'offerte_lavoro'],
    '13': ['Collocamento mirato', u'\U0001F305', 'collocamento_mirato'],
    '15': ['Informazioni di servizio sui CPI', '-', 'info_servizio'],
    '16': ['Bandi e avvisi dai CPI	', '-', 'bandi'],
    '17': ['Statistiche sul mondo del lavoro', '-', 'statistiche'],
    '18': ['Politiche del lavoro', '-', 'politiche_lavoro'],
    '19': ['Tirocini', '-', 'tirocini'],
}

EXT_DEBUG_MSG = True

NEWS_CHECK_PERIOD = 60 * 30  # seconds

MAX_NUM_NEWS_TO_RESEND = 10  # maximum number of news items to resend

SHOW_CATEGORIES_IN_NEWS = True

SHOW_READ_COMMAND_IN_NEWS_BODY = False  # see also message UI_message_read_news_item

# https://unicode.org/emoji/charts/full-emoji-list.html

help_keyword_list =  ['aiuto', 'help', '?']

# chat id for sending bot log messages
BOT_LOGS_CHAT_ID = -358633344

bot_default_help_msg = """Ti aiuto a ricevere notizie ed offerte di lavoro personalizzate sulle tue esigenze.

COMANDI del bot:

<b>/scegli , /categorie</b> per scegliere le categorie di notizie che vuoi ricevere

<b>/privacy</b> lo hai usato per accettare il regolamento privacy

<b>/rimanda_ultime_notizie</b> rimanda le notizie degli ultimi 10 giorni

<b>/statistiche_notizie</b> sulle notizie inviate negli ultimi 10 giorni

<b>/audio_on</b> per abilitare la lettura dei titoli delle notizie. <b>/audio_off</b> per disabilitare la lettura.

<b>/categorie_professionali</b> mostra le frequenze delle parole chiave delle categorie professionali nelle offerte di lavoro pubblicate su http://offertelavoro.regione.fvg.it.

Per mostrare nuovamente questo messaggio digita /help o /aiuto
"""

# removed:
# <b>/start</b> avvio del bot (l'hai già fatto)


def get_bot_default_help_msg():
    return bot_default_help_msg


# DO NOT USE SPACES in string values (required by memcache)
UI_bot_help_message = "UI_bot_help_message"
UI_bot_presentation = "UI_presentazione_bot"
UI_PRIVACY = "UI_PRIVACY"
# UI_request_for_news_item_feedback = "UI_request_for_news_item_feedback"
# UI_select_news_categories = "UI_seleziona_le_categorie_di_news"
RSS_FEED = "RSS_FEED"
CREATE_USER_WITH_ALL_CATEGORIES_SELECTED = "CREATE_USER_WITH_ALL_CATEGORIES_SELECTED"

CURRENT_CONTEXT = 'CURRENT_CONTEXT'

# param_show_match_category_news = "news_mostra_match_categoria"

# UC: upper case
UI_ACCEPT_UC = "ACCETTO"
UI_NOT_ACCEPT_UC = "NON ACCETTO"
UI_CLOSE_UC = 'CHIUDI'


UI_START_COMMAND = 'start'
UI_START_COMMAND_ALT = 'inizia'
UI_HELP_COMMAND = 'help'
UI_HELP_COMMAND_ALT = 'aiuto'
UI_PRIVACY_COMMAND = 'privacy'
UI_UNDO_PRIVACY_COMMAND = 'undo_privacy'
UI_ALL_CATEGORIES_COMMAND = 'tutte_le_notizie'
UI_NO_CATEGORIES_COMMAND = 'nessuna_notizia'
UI_RESEND_LAST_NEWS_COMMAND = 'rimanda_ultime_notizie'
UI_CHOOSE_CATEGORIES_COMMAND = 'scegli'
UI_FORCE_SEND_NEWS_COMMAND = 'update'  # admin only
UI_DEBUG2_COMMAND = 'debug2'  # admin only
UI_DEBUG3_COMMAND = 'debug3'  # admin only
UI_DEBUG4_COMMAND = 'debug4'  # admin only
UI_PING_COMMAND = 'ping'  # admin only
UI_CLEANUP_COMMAND = 'cleanup'  # admin only
UI_SEND_NEWS_COMMAND = 'news'  # admin only
UI_SHOW_NEWS = 'mostra_'  # id of news item is appended
UI_READ_NEWS = 'leggi_'  # id of news item is appended
UI_ME_COMMAND = 'me'
UI_CATEGORIES_HELP = "categorie"
UI_SET_FILTER = "filtro"
UI_STATS_COMMAND = "statistiche_notizie"

UI_AUDIO_ON_COMMAND = "audio_on"
UI_AUDIO_OFF_COMMAND = "audio_off"

UI_SHOW_PROFESSIONAL_CATEGORIES_COMMAND = "categorie_professionali"

UI_message_category = "categoria "

UI_message_disabled_account = "Il tuo account è stato disabilitato dagli amministratori del bot."

UI_message_read_and_accept_privacy_rules_as_follows = "Per proseguire con l'utilizzo di questo bot, " \
                 "è necessario che tu legga ed accetti il regolamento sulla privacy qui riportato:\n\n"

UI_message_accept_privacy_rules_to_continue = 'Prima di proseguire, devi accettare il regolamento per la privacy di questo bot. ' \
            'Usa il comando /privacy per visualizzarlo.'

UI_message_you_have_accepted_privacy_rules_on_this_day = 'hai accettato il regolamento della privacy di questo bot in data '

UI_message_your_privacy_acceptance_has_been_deleted = 'ok, ho cancellato la tua accettazione della privacy.'

UI_message_thank_you_for_accepting_privacy_rules = "Grazie per avere accettato il regolamento della privacy di questo bot.\n"

UI_message_you_have_not_accepted_privacy_rules_cannot_continue = "Non hai accettato il regolamento della privacy di questo bot. Non posso proseguire."

UI_message_you_have_choosen_no_categories = 'Non hai scelto alcuna categoria! Sei proprio sicuro? Non riceverai notizie!\n'

UI_message_you_have_choosen_the_following_categories = 'Grazie, hai scelto le seguenti categorie:\n\n'

UI_message_you_can_modify_categories_with_command = '\nPuoi modificarle in qualsiasi momento usando il comando /scegli .\n' \
                                                    'Se vuoi rivedere le ultime notizie in base alle categorie che hai scelto, usa il comando /rimanda_ultime_notizie'

UI_message_i_have_changed_your_categories = 'Ho cambiato le categorie di notizie che vuoi ricevere, adesso sono:\n'

UI_message_i_have_removed_all_your_categories = 'Ho rimosso tutte le tue categorie di notizie, non ne riceverai.\n'

UI_message_no_previous_news_to_send_again = 'non ho trovato notizie precedenti da rimandarti! ' \
                                            'Se vuoi, puoi provare a cambiare le categorie di notizie che vuoi ricevere con il comando /scegli'
UI_message_no_matching_previous_news = 'non ci sono notizie precedenti che corrispondono alle tue impostazioni. ' \
                                       'Se vuoi, prova a cambiare le categorie di notizie con il comando /scegli e poi riprova /rimanda_ultime_notizie.'

UI_message_thank_you_for_feedback_newline = 'Grazie per il feedback!\n'
UI_message_thank_you_for_feedback = 'Grazie per il feedback!'

UI_message_write_a_comment = 'Vuoi lasciarmi un breve commento su questa notizia? Lo userò per offrirti un servizio migliore.'
UI_message_write_a_comment_button = 'Click per commentare la notizia '

UI_message_comment_to_news_item = 'Commento alla notizia '

UI_message_comment_successful = 'Grazie del commento! Un operatore umano o la mia Intelligenza Artificiale lo leggerà!'

UI_message_thank_you = 'Grazie!'

UI_message_already_resent_news = 'Ti ho già rimandato le ultime notizie poco fa, scorri in alto per vederle. (il limite è di un invio di notizie al minuto)'

UI_message_now_you_can_choose_news_categories = 'Ci siamo quasi!\nOra scegli il tipo di notizie che vuoi ricevere.\n' \
                                                    'Per farlo, usa il comando /scegli.'

UI_arrow = "→"# u"\u2192" #'🠮'

UI_message_select_news_categories = "Seleziona le categorie di notizie a cui sei interessato:\n" + u'\U00002705' + ' → selezionato, ' + \
                                    u'\U0000274C' + ' → non selezionato'

UI_message_ok_suffix = ": Sì"
UI_message_no_suffix = ": No"

UI_message_help_me_provide_better_results = 'Aiutami a darti risultati migliori!\nScrivimi liberamente qualche frase sui tuoi interessi lavorativi.\n' \
                                            'Quello che mi dirai lo darò in pasto alla mia Intelligenza Artificiale :)'

UI_message_do_you_need_examples_on_me_command = 'Vuoi qualche esempio?'

UI_message_let_me_ask_you_some_questions = 'Avanti con le domande!'
UI_message_me_stop_questions = 'Basta così!'

UI_message_do_you_want_news_about = "Vuoi ricevere notizie su <b>{0}</b>?"
UI_message_continue_sending_news_about = "Continuo a mandarti notizie su <b>{0}</b>?"

UI_message_you_are_subscribed_to_news_category = "In questo momento sei iscritto alle notizie su <b>{0}</b>. "
UI_message_you_are_not_subscribed_to_news_category = "In questo momento non sei iscritto alle notizie su <b>{0}</b>. "

UI_message_stop_receive_info_about = "Smetto di mandarti notizie su <b>{0}</b>?"

UI_message_custom_settings_modified_true = 'OK, riceverai le notizie su {0}'
UI_message_custom_settings_modified_false = 'NON riceverai le notizie su {0}'

UI_message_receive_info_about_category = 'ricevi informazioni sulla categoria \'{0}\''

UI_message_no_matching_category_command = 'Non capisco il comando! /aiuto per i comandi del bot.'

UI_message_error_accepting_privacy_rules = "Puoi inserire solo \'{0}\' oppure \'{1}\':"

UI_message_what_is_your_age = 'Per fornirti un servizio migliore, ho bisogno di sapere la tua età.\nQuanti anni hai?'
UI_message_cheers = "Wow! Complimenti per l'età! :)"
UI_message_you_have_provided_your_age = 'Grazie per l\'informazione!'

UI_message_what_is_your_educational_level = 'Ancora una cosa: qual è il tuo titolo di studio più elevato?'
UI_message_enter_custom_educational_level = 'Ok, inserisci il tuo livello di studio'
UI_message_you_have_provided_your_education_level = 'Grazie, hai scelto <i>{0}</i> come livello studio.\n\n'

UI_message_show_complete_news_item = "<b>Per vedere questa notizia completa, fai click qui: /mostra_{0}</b> "

UI_message_read_news_item = "<b>Per la lettura del titolo della notizia, fai click qui: /" + UI_READ_NEWS + "{0}</b>"

UI_message_news_item_category = "categoria della notizia"

UI_message_request_for_news_item_feedback = "Ti è utile questa notizia?"

UI_message_published_on = "pubblicata il"

UI_message_this_is_audio_version_of_news_item = "lettura del titolo della notizia {0}"

UI_message_categories_selection = "inserisci uno dei seguenti comandi per ricevere informazioni riguardo la categoria di notizie:\n"

UI_message_professional_categories_stats = 'offerte di lavoro: parole chiave delle categorie professionali e loro frequenze:\n\n'

UI_news = "notizia"
UI_news_plural = "notizie"

UI_feedback_to_news = "Feedback alle notizie"

UI_comment_to_news = "Commento a notizia"
UI_comment_to_news_plural = "Commenti alle notizie"

UI_files_for_news = "Files per le Notizie"

UI_free_sentences = "frasi libere"
UI_free_sentences_of_telegram_users = "frasi libere degli utenti"

UI_telegram_user = "Utente Telegram"
UI_telegram_users = "Utenti Telegram"

UI_system_parameter = "Parametro di sistema"
UI_system_parameters = "Parametri di sistema"

UI_log_of_interactions_between_bot_and_users = "Log degli scambi tra bot ed utenti"

UI_category = 'Categoria'
UI_categories = 'Categorie'

UI_group_of_categories = 'Gruppo di categorie'
UI_groups_of_categories = 'Gruppi di categorie'

UI_log_of_news_sent_to_users = 'Log delle notizie inviate agli utenti'

UI_statistics_on_news = 'statistiche sulle notizie (negli ultimi 10 giorni):\n'

UI_message_text_to_speech_has_been_enabled = 'lettura audio delle notizie: abilitata'

UI_message_text_to_speech_has_been_disabled = 'lettura audio delle notizie: disabilitata'

UI_external_link = 'collegamento esterno'

UI_OK = 'OK'
UI_NO = 'No'

UI_HELLO = "Ciao"

CALLBACK_INTERNSHIP_OK = 'internship ' + UI_OK
CALLBACK_INTERNSHIP_NO = 'internship ' + UI_NO

UI_broadcast_message = 'comunicazione di servizio a tutti gli utenti'


DATE_FORMAT_STR = '%d-%m-%Y'
# DATE_FORMAT_STR = '%Y-%m-%d'


# show available commands in telegram input box:
# https://stackoverflow.com/questions/34457568/how-to-show-options-in-telegram-bot
'''
aiuto - ti mostro i comandi disponibili
scegli  - scegli le categorie di notizie che vuoi ricevere
rimanda_ultime_notizie - ti rimando le notizie degli ultimi 10 giorni
statistiche_notizie - quante notizie inviate negli ultimi 10 giorni, per categoria
categorie_professionali - ti mostro le categorie professionali delle offerte di lavoro
'''
#privacy - accetta il regolamento sulla privacy di questo bot


# two newlines (\n) to separate the subject from the message body
DEFAULT_EMAIL_TEMPLATE = """\
Subject: {0}
To: {1}
From: {2}

{3}"""

