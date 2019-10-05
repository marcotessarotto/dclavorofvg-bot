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
    '11': ['Garanzia giovani', u'\U00002705']
}


# def get_categories_dict():
#     return DEFAULT_CATEGORY_DICT

bot_default_help_msg = 'Attraverso questo bot potrai ricevere news sul mondo del lavoro personalizzate sulle tue esigenze.\n' \
    '\n' \
    'Se sei interessato principalmente al mondo del lavoro, allora puoi usare il comando <b>/lavoro</b>.\n' \
    '\n' \
    'Se sei interessato principalmente alle offerte di lavoro, usa il comando <b>/offerte_di_lavoro</b>.\n' \
    '\n' \
    'Se sei interessato principalmente alle proposte per i giovani, usa il comando <b>/giovani</b>.\n' \
    '\n' \
    'Per specificare più in dettaglio le aree di interesse, usa il comando <b>/scegli</b>.\n' \
    '\n' \
    'Questi sono i comandi a disposizione:\n' \
    '\n' \
    '<b>/start</b> schermata iniziale del bot\n' \
    '<b>/scegli</b> scegli le categorie di notizie che ti interessano\n' \
    '<b>/privacy</b> gestisci l\'accettazione della privacy\n' \
    '\n' \
    '<b>/invia_ultime_news</b> invia le ultime news\n' \
    '\n' \
    'Per avviare un comando digitalo da tastiera oppure selezionalo dalla lista.\n' \
    'Per mostrare nuovamente questo messaggio digita /help o /aiuto o /start'


def get_bot_default_help_msg():
    return bot_default_help_msg


# DO NOT USE SPACES (for memcache)
UI_bot_help_message = "UI_bot_help_message"
UI_bot_presentation = "UI_presentazione_bot"
UI_PRIVACY = "UI_PRIVACY"
UI_request_for_news_item_feedback = "UI_request_for_news_item_feedback"
UI_select_news_categories = "UI_seleziona_le_categorie_di_news"

param_show_match_category_news = "news_mostra_match_categoria"