from django.db import models

import traceback
import logging

# from spacy.lang.fr.tokenizer_exceptions import verb
from .definitions import *


class CustomDateTimeField(models.DateTimeField):
    def value_to_string(self, obj):
        val = self.value_from_object(obj)
        if val:
            val.replace(microsecond=0)
            return val.isoformat()
        return ''


# ****************************************************************************************
class Category(models.Model):
    """ Classe CATEGORY: rappresenta le informazioni legate alle categorie """

    key = models.CharField(max_length=2)
    name = models.CharField(max_length=256)
    emoji = models.CharField(max_length=9, blank=True, null=True)
    description = models.CharField(max_length=256, blank=True, null=True, verbose_name="descrizione")

    is_telegram_command = models.BooleanField(default=True, verbose_name="comando telegram dedicato?")
    custom_telegram_command = models.CharField(max_length=64, blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorie'
        app_label = 'backoffice'

    def __str__(self):
        return str(self.key) + ' (' + \
               str(self.name) + ') ' + str(self.emoji)

    # fills the Category table (if it is empty) with some default cateogries stored in the dict
    @staticmethod
    def fill_categories():
        from .definitions import DEFAULT_CATEGORY_DICT

        for key in DEFAULT_CATEGORY_DICT:

            if len(Category.objects.filter(key=key)) != 0:
                continue

            k = Category()

            k.key = key
            k.name = DEFAULT_CATEGORY_DICT[key][0]
            k.emoji = DEFAULT_CATEGORY_DICT[key][1]
            k.save()

        return True


class CategoriesGroup(models.Model):
    name = models.CharField(max_length=256,verbose_name="Nome del gruppo")
    updated_at = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(Category, blank=True)
    add_bot_command = models.BooleanField(default=True, verbose_name="aggiungi automaticamente comando bot con stesso nome")

    class Meta:
        verbose_name = 'Gruppo di categorie'
        verbose_name_plural = 'Gruppi di categorie'
        app_label = 'backoffice'

    def __str__(self):
        return str(self.id) + " " + self.name + " (" + str(self.categories) + ")"


class NewsItemSentToUser(models.Model):
    telegram_user = models.ForeignKey('TelegramUser', on_delete=models.CASCADE)
    news_item = models.ForeignKey('NewsItem', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    flags = models.CharField(max_length=4, blank=True, null=True, )

    def __str__(self):
        return str(self.id) + " user=" + str(self.telegram_user.id) + " news_id=" + str(self.news_item.id) + " " + str(self.flags)

    class Meta:
        verbose_name = 'NewsItemSentToUser'
        verbose_name_plural = 'NewsItemSentToUser'
        app_label = 'backoffice'


# ****************************************************************************************
class TelegramUser(models.Model):
    """ Classe TELEGRAMUSER: rappresenta le informazioni legate agli utenti Telegram """

    user_id = models.BigIntegerField(verbose_name="telegram user id")  # Telegram used id

    regionefvg_id = models.BigIntegerField(default=-1,verbose_name="internal use", editable=False)  # for internal use

    rss_id = models.CharField(max_length=256, blank=True, null=True, editable=False) # used if news comes from rss feed

    has_accepted_privacy_rules = models.BooleanField(default=False, verbose_name="ha accettato il regolamento privacy?")
    # L : through a parameter passed to /start
    # U : user must accept privacy rules
    privacy_acceptance_mechanism = models.CharField(max_length=1, blank=True, null=True, verbose_name="meccanismo di accettazione privacy (U: tramite il bot)")
    privacy_acceptance_timestamp = models.DateTimeField(blank=True, null=True)

    username = models.CharField(max_length=32, blank=True, null=True)

    first_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Nome")
    last_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Cognome")

    is_bot = models.BooleanField(default=False, verbose_name="è un bot?")

    language_code = models.CharField(max_length=2, blank=True, null=True)

    categories = models.ManyToManyField(Category, blank=True, verbose_name="categorie")

    number_of_received_news_items = models.BigIntegerField(default=0, verbose_name="numero di news ricevute")

    # receive_intership_information = models.BooleanField(default=True, verbose_name="vuole ricevere informazioni sui tirocini?")
    #
    # receive_courses_information = models.BooleanField(default=True, verbose_name="vuole ricevere informazioni sui corsi?")
    #
    # receive_recruiting_days_information = models.BooleanField(default=True, verbose_name="vuole ricevere informazioni sui recruiting day?")
    #
    # receive_targeted_placement_information = models.BooleanField(default=False, verbose_name="vuole ricevere informazioni dal collocamento mirato?")

    def categories_str(self):
        result = ''
        for cat in self.categories.all():
            result += '- ' + cat.name + '  ' + cat.emoji + '\n'
        return result

    enabled = models.BooleanField(default=True, verbose_name="abilitato")

    # when loading TelegramUser, use defer()
    # https://docs.djangoproject.com/en/2.2/ref/models/querysets/#defer
    #news_item_sent_to_user = models.ManyToManyField(NewsItemSentToUser, blank=True)

    is_admin = models.BooleanField(default=False, verbose_name="amministratore del bot?")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Utente Telegram"
        verbose_name_plural = "Utenti Telegram"
        app_label = "backoffice"

    def __str__(self):
        return 'user ' + str(self.user_id) + ' (' + \
               str(self.first_name) + ' ' + str(self.last_name) + ')'


# ****************************************************************************************
class NewsFile(models.Model):
    file_field = models.FileField(upload_to='uploads/%Y/%m/%d/')
    upload_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "backoffice"
        verbose_name = "Files per News"
        verbose_name_plural = "Files per News"

    def __str__(self):
        return "" + str(self.id) + ": " + self.file_field.name + ", caricato il " + self.upload_date.strftime(
            "%d/%m/%y")


class NewsItem(models.Model):
    """ Classe NEWSITEM: rappresenta le informazioni legati agli item di una news """

    #news_id = models.CharField(max_length=5, blank=True, null=True)

    title = models.CharField(max_length=1024, blank=True, null=True, verbose_name='titolo della news')
    title_link = models.CharField(max_length=1024, blank=True, null=True, verbose_name='link (opzionale) a cui punta il titolo')

    text = models.TextField(max_length=1024*2, blank=True, null=True, verbose_name="testo della news (max 2048 caratteri)")

    show_all_text = models.BooleanField(default=True, verbose_name="mostra tutto il testo della news all'utente?")
    show_first_n_words = models.IntegerField(default=30, verbose_name="mostra le prime n parole")

    categories = models.ManyToManyField(Category,  blank=True, verbose_name="categorie")

    broadcast_message = models.BooleanField(default=False, verbose_name='forza l\'invio a tutti gli utenti')

    link = models.CharField(max_length=1024, blank=True, null=True)
    link_caption = models.CharField(max_length=1024, blank=True, null=True, default="continua")

    file1 = models.ForeignKey(NewsFile, on_delete=models.PROTECT, null=True, blank=True, verbose_name="immagine")
    file2 = models.ForeignKey(NewsFile, related_name="file2", on_delete=models.PROTECT, null=True, blank=True, verbose_name="allegato 1")
    file3 = models.ForeignKey(NewsFile, related_name="file3", on_delete=models.PROTECT, null=True, blank=True, verbose_name="allegato 2")

    # https://docs.djangoproject.com/en/2.2/ref/models/fields/#django.db.models.FileField
    # file will be saved to MEDIA_ROOT/uploads/....
    # attached_files = models.ManyToManyField(NewsFile,  blank=True)

    like = models.BigIntegerField(default=0, editable=False)
    dislike = models.BigIntegerField(default=0, editable=False)

    start_publication = models.DateTimeField(blank=True, null=True, verbose_name="data di invio (opzionale: se non specificata, la news verrà inviata appena possibile)")
    # end_publication = models.DateTimeField(blank=True, null=True, verbose_name="fine periodo di pubblicazione")

    recurrent_for_new_users = models.BooleanField(default=False, verbose_name="invia questa news ad ogni nuovo utente del bot?")

    # if processed is true, this news item has already been sent to all users
    processed = models.BooleanField(default=False, editable=True, verbose_name="questa news è stata inviata agli utenti?")
    processed_timestamp = models.DateTimeField(blank=True, null=True, editable=False, verbose_name='data di elaborazione')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='data inserimento')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "News"
        verbose_name_plural = "News"
        app_label = "backoffice"

    def __str__(self):
        return 'news #' + str(self.id) + ' (' + \
               str(self.title) + ')'


# ****************************************************************************************
class Comment(models.Model):
    """ Class COMMENT: rappresenta i commenti lasciati dagli utenti """

    news = models.ForeignKey(NewsItem, on_delete=models.PROTECT, null=True)
    user = models.ForeignKey(TelegramUser, on_delete=models.PROTECT, null=True)

    text = models.TextField(max_length=4096, verbose_name='commento')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Commento"
        verbose_name_plural = "Commenti"
        app_label = "backoffice"

    def __str__(self):
        return "Comment FOR " + \
               str(self.news) + " FROM " + \
               str(self.user)


# ****************************************************************************************
# Non ho ben capito che utilità abbia questa classe
class CommandsFromUser(models.Model):
    telegramUser = models.ForeignKey(TelegramUser, on_delete=models.PROTECT)

    command = models.CharField(max_length=256)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "backoffice"


class UserActivityLog(models.Model):
    user_id = models.BigIntegerField()
    news_id = models.BigIntegerField()

    value = models.CharField(max_length=1, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "backoffice"


class SystemParameter(models.Model):
    name = models.CharField(max_length=256, blank=False)

    value = models.TextField(max_length=4096, blank=False)

    comment = models.CharField(max_length=256, blank=True, editable=False)

    # @staticmethod
    # def add_default_param(name):
    #     k = SystemParameter()
    #     k.name = name
    #     k.value = "***" + name + "***"
    #     k.save()

    @staticmethod
    def add_default_param(name, value, comment=""):

        queryset = SystemParameter.objects.filter(name=name)

        if len(queryset) == 0:

            k = SystemParameter()
            k.name = name
            k.value = value
            k.comment = comment
            k.save()

    @staticmethod
    def update_system_parameters():
        # if len(SystemParameter.objects.all()) == 0:

        SystemParameter.add_default_param(UI_PRIVACY, "TODO: inserire regolamento privacy del bot/portale/...", "regolamento della privacy")

        SystemParameter.add_default_param(UI_select_news_categories, "Seleziona le categorie di news a cui sei interessato:")

        SystemParameter.add_default_param(UI_bot_presentation, "Benvenuto al bot Telegram della Direzione centrale lavoro, formazione, istruzione e famiglia - Regione Autonoma Friuli Venezia Giulia :)", "è mostrato nel comando /start")

        SystemParameter.add_default_param("DEBUG_SEND_NEWS", "False", "non setta come processati le news item")

        SystemParameter.add_default_param(UI_bot_help_message, get_bot_default_help_msg(), "è mostrato nel comando /help")

        SystemParameter.add_default_param(UI_request_for_news_item_feedback, "Ti è utile questa news?", "messaggio all'utente per chiedere feedback dopo aver ricevuto una news")

        SystemParameter.add_default_param(param_show_match_category_news, "True", "mostra la categoria della news che ha permesso l'invio all'utente")

        SystemParameter.add_default_param(RSS_FEED, "http://www.regione.fvg.it/rafvg/cms/RAFVG/formazione-lavoro/servizi-lavoratori/news/?rss=y", "rss feed to watch")

        return True

    class Meta:
        verbose_name = "Parametro di sistema"
        verbose_name_plural = "Parametri di sistema"
        app_label = "backoffice"

    def __str__(self):
        return str(self.name)
