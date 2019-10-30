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
    '02': ['Studio, formazione e corsi', u'\U0001F4DA', 'formazione'],
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

# https://unicode.org/emoji/charts/full-emoji-list.html

help_keyword_list =  ['aiuto', 'help', '?']

bot_default_help_msg = """Ti aiuto a ricevere news ed offerte di lavoro personalizzate sulle tue esigenze.

Aiutami a fornirti risultati migliori per te! Usa il comando /me

Se vuoi ricevere tutte le news, usa il comando <b>/tutte_le_news</b>.
Se non vuoi ricevere nessuna news, usa il comando <b>/nessuna_news</b>.

Per specificare più in dettaglio le aree di interesse, usa il comando <b>/scegli</b>.

<b>/help_categorie</b>  

Questi sono i comandi a disposizione:

<b>/start</b> schermata iniziale del bot
<b>/scegli</b> scegli le categorie di notizie che ti interessano
<b>/privacy</b> gestisci l'accettazione della privacy

<b>/rimanda_ultime_news</b> rimanda le ultime news

Per avviare un comando digitalo da tastiera oppure selezionalo dalla lista.
Per mostrare nuovamente questo messaggio digita /help o /aiuto o /start"""


def get_bot_default_help_msg():
    return bot_default_help_msg


# DO NOT USE SPACES (for memcache)
UI_bot_help_message = "UI_bot_help_message"
UI_bot_presentation = "UI_presentazione_bot"
UI_PRIVACY = "UI_PRIVACY"
UI_request_for_news_item_feedback = "UI_request_for_news_item_feedback"
# UI_select_news_categories = "UI_seleziona_le_categorie_di_news"
RSS_FEED = "RSS_FEED"

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
UI_ALL_CATEGORIES_COMMAND = 'tutte_le_news'
UI_NO_CATEGORIES_COMMAND = 'nessuna_news'
UI_RESEND_LAST_NEWS_COMMAND = 'rimanda_ultime_news'
UI_CHOOSE_CATEGORIES_COMMAND = 'scegli'
UI_DEBUG_COMMAND = 'debug' # admin only
UI_DEBUG2_COMMAND = 'debug2' # admin only
UI_DEBUG3_COMMAND = 'debug3' # admin only
UI_SEND_NEWS_COMMAND = 'news' # admin only
UI_SHOW_NEWS = 'mostra_' # id of news item is appended
UI_ME_COMMAND = 'me'
UI_CATEGORIES_HELP = "help_categorie"

UI_message_category = "categoria "

UI_message_disabled_account = "Il tuo account è stato disabilitato dagli amministratori del bot."

UI_message_read_and_accept_privacy_rules_as_follows = "Per proseguire con l'utilizzo di questo bot, " \
                 "è necessario che tu legga ed accetti il regolamento sulla privacy qui di seguito riportato:\n"

UI_message_accept_privacy_rules_to_continue = 'Prima di proseguire, devi accettare il regolamento per la /privacy di questo bot.\n' \
            'Usa il comando /privacy per visualizzare il regolamento.'

UI_message_you_have_accepted_privacy_rules_on_this_day = 'hai accettato il regolamento della privacy di questo bot in data '

UI_message_your_privacy_acceptance_has_been_deleted = 'ok, ho cancellato la tua accettazione della privacy.'

UI_message_thank_you_for_accepting_privacy_rules = "Grazie per avere accettato il regolamento della privacy di questo bot.\n"

UI_message_you_have_not_accepted_privacy_rules_cannot_continue = "Non hai accettato il regolamento della privacy di questo bot. Non posso proseguire."

UI_message_you_have_choosen_no_categories = 'Non hai scelto alcuna categoria! Sei proprio sicuro? Non riceverai notizie!\n'

UI_message_you_have_choosen_the_following_categories = 'Grazie, hai scelto le seguenti categorie:\n\n'

UI_message_you_can_modify_categories_with_command = '\nPuoi modificarle in qualsiasi momento usando il comando /scegli .'

UI_message_i_have_changed_your_categories = 'Ho cambiato le categorie di news che vuoi ricevere, adesso sono:\n'

UI_message_i_have_removed_all_your_categories = 'Ho rimosso tutte le tue categorie di news, non ne riceverai.\n'

UI_message_no_previous_news_to_send_again = 'non ho trovato notizie precedenti da rimandarti! ' \
                                            'Se vuoi, puoi provare a cambiare le categorie di notizie che vuoi ricevere con il comando /scegli'
UI_message_no_matching_previous_news = 'non ci sono news precedenti che corrispondono alle tue impostazioni. ' \
                                       'Se vuoi, prova a cambiare le categorie di news con il comando /scegli e poi riprova /rimanda_ultime_news.'

UI_message_thank_you_for_feedback_newline = 'Grazie per il feedback!\n'
UI_message_thank_you_for_feedback = 'Grazie per il feedback!'

UI_message_write_a_comment = 'Scrivi un commento'

UI_message_comment_to_news_item = 'Commento alla news {0}'

UI_message_comment_successful = 'Grazie del commento! Un operatore umano o la mia Intelligenza Artificiale lo leggerà!'

UI_message_thank_you = 'Grazie!'

UI_message_already_resent_news = 'Ti ho già rimandato le ultime notizie poco fa, scorri in alto per vederle. (il limite è di un invio di notizie al minuto)'

UI_message_cheers = "Wow! Complimenti per l'età! :)"

UI_message_you_have_provided_your_education_level = 'Grazie, hai scelto \'{0}\' come livello studio.\n\n'

UI_message_now_you_can_choose_news_categories = 'Ci siamo quasi!\nOra scegli il tipo di news che vuoi ricevere.\n' \
                                                    'Per farlo, usa il comando /scegli.'

UI_message_select_news_categories = "Seleziona le categorie di news a cui sei interessato:"

UI_message_ok_suffix = ": Sì"
UI_message_no_suffix = ": No"

UI_message_help_me_provide_better_results = 'Aiutami a darti risultati migliori!\nScrivimi liberamente qualche frase sui tuoi interessi lavorativi.\n' \
                                            'Quello che mi dirai lo darò in pasto alla mia Intelligenza Artificiale :)'

UI_message_do_you_need_examples_on_me_command = 'Vuoi qualche esempio?'

UI_message_let_me_ask_you_some_questions = 'Avanti con le domande!'
UI_message_me_stop_questions = 'Basta così!'

UI_message_do_you_want_news_about = "Vuoi ricevere news su <b>{0}</b>?"
UI_message_continue_sending_news_about = "Continuo a mandarti news su <b>{0}</b>?"

UI_message_you_are_subscribed_to_news_category = "In questo momento sei iscritto alle news su <b>{0}</b>. "
UI_message_you_are_not_subscribed_to_news_category = "In questo momento non sei iscritto alle news su <b>{0}</b>. "

UI_message_stop_receive_info_about = "Smetto di mandarti news su <b>{0}</b>?"

UI_message_custom_settings_modified_true = 'OK, riceverai le news su {0}'
UI_message_custom_settings_modified_false = 'NON riceverai le news su {0}'

UI_message_receive_info_about_category = 'ricevi informazioni sulla categoria \'{0}\''

UI_message_no_matching_category_command = 'non capisco il comando! /aiuto per i comandi del bot.'

UI_message_what_is_your_age = 'Per fornirti un servizio migliore, ho bisogno di sapere la tua età.\nQuanti anni hai?'

UI_message_what_is_your_educational_level = 'Ancora una cosa: per fornirti un servizio migliore, ho bisogno di sapere il tuo titolo di studio più elevato:'

UI_message_show_complete_news_item = "Per vedere questa notizia completa, fai click qui: /mostra_{0}"


UI_OK = 'OK'
UI_NO = 'No'

CALLBACK_INTERNSHIP_OK = 'internship ' + UI_OK
CALLBACK_INTERNSHIP_NO = 'internship ' + UI_NO

UI_broadcast_message = 'comunicazione di servizio a tutti gli utenti'

DATE_FORMAT_STR = '%d-%m-%Y'
# DATE_FORMAT_STR = '%Y-%m-%d'


# show available commands in telegram input box:
# https://stackoverflow.com/questions/34457568/how-to-show-options-in-telegram-bot
'''
help - mostra i comandi disponibili
offerte_di_lavoro - che tipo di  offerte di lavoro vuoi ricevere?
scegli  - scegli che tipo di news vuoi ricevere
privacy - accetta il regolamento sulla privacy di questo bot
tirocini - ricevi (o no) info sui tirocini
corsi - ricevi (o no) info sui corsi
me - aiutami a fornirti risultati su misura per te
impostazioni - mostra tutte le impostazioni utente
'''

