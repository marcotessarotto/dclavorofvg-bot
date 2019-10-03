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


bot_default_help_msg = 'Questi sono i comandi a disposizione:\n' \
           '\n' \
           '<b>/start</b> schermata iniziale del bot\n' \
           '<b>/scegli</b> scegli le categorie di notizie che ti interessano\n' \
           '<b>/privacy</b> gestisci l\'accettazione della privacy\n' \
           '\n' \
           '<b>***SOLO PER DEBUG***: /invia_articoli</b> invia l\'articolo di prova\n' \
           '\n' \
           'Per avviare un comando digitalo da tastiera oppure selezionalo dalla lista.\n' \
           'Per mostrare nuovamente questo messaggio digita /help o /aiuto o /start'


def get_bot_default_help_msg():
    return bot_default_help_msg
