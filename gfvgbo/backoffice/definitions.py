# Dizionario contenente le categorie tra cui scegliere
# Colonna 1 -> Nome categoria
# Colonna 2 -> Checked/Unchecked
# Colonna 3 -> Emoji
category_dict = {
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


def get_categories_dict():
    return category_dict
