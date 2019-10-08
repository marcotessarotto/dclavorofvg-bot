# Dizionario contenente le categorie tra cui scegliere
# Colonna 1 -> Nome categoria
# Colonna 2 -> Checked/Unchecked
# Colonna 3 -> Emoji
DEFAULT_CATEGORY_DICT = {
    '01': ['Lavoro', u'\U0001F4BC'],
    '02': ['Studio e formazione', u'\U0001F4DA'],
    '03': ['Mobilità all’estero', u'\U00002708'],
    '04': ['Associazionismo e partecipazione', u'\U0001F465'],
    '05': ['Casa e servizi alla persona', u'\U0001F3E0'],
    '06': ['Eventi e tempo libero', u'\U0001F3AD'],
    '07': ['Star bene', u'\U0001F9D8'],
    '08': ['Giovani eccellenze in FVG', u'\U0001F393'],
    '09': ['La regione FVG per i giovani', u'\U0001F91D'],
    '10': ['Studi e ricerche mondo giovani', u'\U0001F4DD'],
    '11': ['Garanzia giovani', u'\U0001F3DB'],
    '12': ['Offerte di lavoro', u'\U0001F3D7']
}


bot_default_help_msg = """Potrai ricevere news sul mondo del lavoro personalizzate sulle tue esigenze.

Se sei interessato principalmente alle offerte di lavoro, usa il comando <b>/offerte_di_lavoro</b>.

Se sei interessato principalmente alle proposte per i giovani, usa il comando <b>/giovani</b>.

Se vuoi ricevere tutte le news, usa il comando <b>/tutte_le_news</b>.

Se non vuoi ricevere nessuna news, usa il comando <b>/nessuna_news</b>.

Per specificare più in dettaglio le aree di interesse, usa il comando <b>/scegli</b>.

Questi sono i comandi a disposizione:

<b>/start</b> schermata iniziale del bot
<b>/scegli</b> scegli le categorie di notizie che ti interessano
<b>/privacy</b> gestisci l'accettazione della privacy

<b>/rimanda_ultime_news</b> rimanda le ultime news

Per avviare un comando digitalo da tastiera oppure selezionalo dalla lista.
Per mostrare nuovamente questo messaggio digita /help o /aiuto o /start"""

print(bot_default_help_msg)


def get_bot_default_help_msg():
    return bot_default_help_msg


# DO NOT USE SPACES (for memcache)
UI_bot_help_message = "UI_bot_help_message"
UI_bot_presentation = "UI_presentazione_bot"
UI_PRIVACY = "UI_PRIVACY"
UI_request_for_news_item_feedback = "UI_request_for_news_item_feedback"
UI_select_news_categories = "UI_seleziona_le_categorie_di_news"

param_show_match_category_news = "news_mostra_match_categoria"

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
UI_VACANCIES_COMMAND = 'offerte_di_lavoro'
UI_YOUNG_COMMAND = 'giovani'
UI_ALL_CATEGORIES_COMMAND = 'tutte_le_news'
UI_NO_CATEGORIES_COMMAND = 'nessuna_news'
UI_RESEND_LAST_NEWS_COMMAND = 'rimanda_ultime_news'
UI_CHOOSE_CATEGORIES_COMMAND = 'scegli'
UI_DEBUG_COMMAND = 'debug'
UI_DETACH_BOT = 'fine'


UI_message_read_and_accept_privacy_rules_as_follows = "Per proseguire con l'utilizzo di questo bot, " \
                 "è necessario che tu legga ed accetti il regolamento sulla privacy qui di seguito riportato:\n"

UI_message_accept_privacy_rules_to_continue = 'Prima di proseguire, devi accettare il regolamento per la /privacy di questo bot.\n' \
            'Usa il comando /privacy per visualizzare il regolamento.'

UI_message_you_have_accepted_privacy_rules_on_this_day = 'hai accettato il regolamento della privacy di questo bot in data '

UI_message_your_privacy_acceptance_has_been_deleted = 'ok, ho cancellato la tua accettazione della privacy.'

UI_message_thank_you_for_accepting_privacy_rules = "Grazie per avere accettato il regolamento della privacy di questo bot.\n"

UI_message_you_have_not_accepted_privacy_rules_cannot_continue = "Non hai accettato il regolamento della privacy di questo bot. Non posso proseguire."

UI_message_you_have_choosen_no_categories = 'Non hai scelto alcuna categoria.\n'

UI_message_you_have_choosen_the_following_categories = 'Grazie, hai scelto le seguenti categorie:\n\n'

UI_message_you_can_modify_categories_with_command = '\nPuoi modificarle in qualsiasi momento usando il comando /scegli .'

UI_message_i_have_changed_your_categories = 'Ho cambiato le categorie di news che vuoi ricevere, adesso sono:\n'

UI_message_i_have_removed_all_your_categories = 'Ho rimosso tutte le tue categorie di news, non ne riceverai.\n'

UI_message_no_previous_news_to_send_again = 'non ci sono news precedenti da rimandare!'
UI_message_no_matching_previous_news = 'non ci sono news precedenti che corrispondono alle tue impostazioni. ' \
                                       'Se vuoi, prova a cambiare le categorie di news con il comando /scegli e poi riprova /rimanda_ultime_news.'

UI_message_thank_you_for_feedback_newline = 'Grazie per il feedback!\n'
UI_message_thank_you_for_feedback = 'Grazie per il feedback!'

UI_message_write_a_comment = 'Scrivi un commento'

UI_message_comment_to_news_item = 'Commento alla news {0}'

UI_message_comment_successful = 'Commento caricato con successo!'

UI_broadcast_message = 'comunicazione di servizio'

DATE_FORMAT_STR = '%d-%m-%Y'
# DATE_FORMAT_STR = '%Y-%m-%d'


# show available commands in telegram input box:
# https://stackoverflow.com/questions/34457568/how-to-show-options-in-telegram-bot
'''
help - mostra i comandi disponibili
offerte_di_lavoro - iscriviti a ricevere news su offerte di lavoro
giovani - iscriviti a ricevere news sul tema dei giovani e lavoro
scegli  - scegli in dettaglio che tipo di news vuoi ricevere
privacy - accetta il regolamento sulla privacy di questo bot

'''

