from django.db import models

from .definitions import *


class CustomDateTimeField(models.DateTimeField):
    def value_to_string(self, obj):
        val = self.value_from_object(obj)
        if val:
            val.replace(microsecond=0)
            return val.isoformat()
        return ''


APP_LABEL = "backoffice"  # DO NOT MODIFY


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
        verbose_name = UI_category
        verbose_name_plural = UI_categories
        app_label = APP_LABEL

    def __str__(self):
        return UI_message_category + str(self.key) + ' (' + \
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
            k.custom_telegram_command = DEFAULT_CATEGORY_DICT[key][2]
            k.save()

        return True


class CategoriesGroup(models.Model):
    name = models.CharField(max_length=256,verbose_name="Nome del gruppo")
    updated_at = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(Category, blank=True)
    add_bot_command = models.BooleanField(default=True, verbose_name="aggiungi automaticamente comando bot con stesso nome")

    class Meta:
        verbose_name = UI_group_of_categories
        verbose_name_plural = UI_groups_of_categories
        app_label = APP_LABEL

    def __str__(self):
        return str(self.id) + " " + self.name + " (" + str(self.categories) + ")"


class NewsItemSentToUser(models.Model):
    telegram_user = models.ForeignKey('TelegramUser', on_delete=models.CASCADE)
    news_item = models.ForeignKey('NewsItem', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    flags = models.CharField(max_length=4, blank=True, null=True, )

    def __str__(self):
        return str(self.id) + " - user(id=" + str(self.telegram_user.id) + "/telegram_id=" + str(self.telegram_user.user_id) + "), " \
                              "news_id=" + str(self.news_item.id) + ", flags=" + str(self.flags) + " sent=" + self.created_at.strftime("%d/%m/%y")

    class Meta:
        verbose_name = UI_log_of_news_sent_to_users
        verbose_name_plural = UI_log_of_news_sent_to_users
        app_label = APP_LABEL


# ****************************************************************************************

EDUCATIONAL_LEVELS = (
    ('-', 'non dichiarato'),
    ('0', 'nessun titolo di studio'),
    ('a', 'scuola elementare'),
    ('b', 'scuola media'),
    ('c', 'scuola superiore'),
    ('d', 'corsi pre-universitari/brevi corsi professionali' ),
    ('e', 'laurea/laurea magistrale' ),
    ('f', 'dottorato di ricerca' ),
    ('g', 'altro')
)


class TelegramUser(models.Model):
    """ Classe TELEGRAMUSER: rappresenta le informazioni legate agli utenti Telegram """

    user_id = models.BigIntegerField(verbose_name="telegram user id")  # Telegram used id (information provided by Telegram)

    age = models.IntegerField(default=-1, verbose_name="età")

    educational_level = models.CharField(max_length=1, choices=EDUCATIONAL_LEVELS, default='-', verbose_name="titolo di studio più elevato")

    chat_state = models.CharField(max_length=1, default = '-', blank=True, editable=False)

    regionefvg_id = models.BigIntegerField(default=-1,verbose_name="internal use", editable=False)  # for internal use

    has_accepted_privacy_rules = models.BooleanField(default=False, verbose_name="ha accettato il regolamento privacy?")
    # L : through a parameter passed to /start
    # U : user has accepted privacy rules through bot UI
    privacy_acceptance_mechanism = models.CharField(max_length=1, blank=True, null=True, editable=False, verbose_name="meccanismo di accettazione privacy (U: tramite il bot)")
    privacy_acceptance_timestamp = models.DateTimeField(blank=True, null=True)

    username = models.CharField(max_length=32, blank=True, null=True)  # information provided by Telegram

    first_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Nome")
    last_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Cognome")

    is_bot = models.BooleanField(default=False, verbose_name="è un bot?")  # information provided by Telegram

    language_code = models.CharField(max_length=2, blank=True, null=True)  # information provided by Telegram

    categories = models.ManyToManyField(Category, blank=True, verbose_name="categorie")

    number_of_received_news_items = models.BigIntegerField(default=0, verbose_name="numero di news ricevute")

    #resend_news_timestamp = models.DateTimeField(blank=True, null=True, editable=False)

    def categories_str(self):
        result = ''
        for cat in self.categories.all():
            if cat.emoji is not None:
                result += '- ' + cat.name + '  ' + cat.emoji + '\n'
            else:
                result += '- ' + cat.name + '\n'
        return result

    enabled = models.BooleanField(default=True, verbose_name="utente abilitato all'uso del bot")  # user can be disabled by bot admins

    # when loading TelegramUser, use defer()
    # https://docs.djangoproject.com/en/2.2/ref/models/querysets/#defer
    #news_item_sent_to_user = models.ManyToManyField(NewsItemSentToUser, blank=True)

    is_admin = models.BooleanField(default=False, verbose_name="amministratore del bot")  # is bot admin?

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def educational_level_verbose(self):
        return dict(EDUCATIONAL_LEVELS)[self.educational_level]

    class Meta:
        verbose_name = UI_telegram_user
        verbose_name_plural = UI_telegram_users
        app_label = "backoffice"

    def __str__(self):
        return 'user ' + str(self.user_id) + ' (' + \
               str(self.first_name) + ' ' + str(self.last_name) + ')'


class UserFreeText(models.Model):  #
    text = models.CharField(max_length=1024, blank=True, null=True)
    telegram_user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'UserFreeText ' + str(self.telegram_user.user_id) + ' : ' + self.text

    class Meta:
        verbose_name = UI_free_sentences
        verbose_name_plural = UI_free_sentences_of_telegram_users
        app_label = "backoffice"


class RssFeedItem(models.Model):
    rss_id = models.CharField(max_length=1024, blank=True, null=True)
    rss_title = models.CharField(max_length=1024, blank=True, null=True, verbose_name="titolo")
    rss_link = models.CharField(max_length=1024, blank=True, null=True, verbose_name="link")
    updated_parsed = models.DateTimeField(blank=True, null=True, editable=False, )

    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.CASCADE, verbose_name="categoria")

    processed = models.BooleanField(default=False, editable=True,
                                    verbose_name="trasformato in news")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='data inserimento')

    def __str__(self):
        return 'RssFeedItem ' + str(self.id) + ' : ' + str(self.data_feed_was_last_updated()) + ' - ' + str(self.category) + ' - ' + str(self.rss_title)

    def data_feed_was_last_updated(self):
        return str(self.updated_parsed.strftime("%d/%m/%y"))

    class Meta:
        verbose_name = "RssFeedItem"
        app_label = "backoffice"


class NewsFile(models.Model):
    file_field = models.FileField(upload_to='uploads/%Y/%m/%d/')
    upload_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "backoffice"
        verbose_name = UI_files_for_news
        verbose_name_plural = UI_files_for_news

    def __str__(self):
        return "" + str(self.id) + " : " + self.file_field.name + "" + self.upload_date.strftime(
            "%d/%m/%y")


class NewsItem(models.Model):
    """ Classe NEWSITEM: rappresenta le informazioni legati agli item di una news """

    title = models.CharField(max_length=1024, blank=True, null=True, verbose_name='titolo della news')
    title_link = models.CharField(max_length=1024, blank=True, null=True, verbose_name='link (opzionale) a cui punta il titolo')

    text = models.TextField(max_length=2048, blank=True, null=True, verbose_name="testo della news (max 2048 caratteri)")

    show_all_text = models.BooleanField(default=True, verbose_name="mostra tutto il testo della news all'utente?")
    show_first_n_words = models.IntegerField(default=30, verbose_name="mostra le prime n parole")

    categories = models.ManyToManyField(Category,  blank=True, verbose_name="categorie")

    # broadcast_message: if True, this message will be sent to all users without considering matching categories
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

    rss_id = models.CharField(max_length=256, blank=True, null=True, editable=False)  # used if news comes from rss feed

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='data inserimento')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = UI_news
        verbose_name_plural = UI_news_plural
        app_label = "backoffice"

    def __str__(self):
        return 'news #' + str(self.id) + ' (' + \
               str(self.title) + ')'
        return f"news #{self.id} "


class FeedbackToNewsItem(models.Model):
    news = models.ForeignKey(NewsItem, on_delete=models.PROTECT, null=True)
    user = models.ForeignKey(TelegramUser, on_delete=models.PROTECT, null=True)
    val = models.SmallIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = UI_feedback_to_news
        verbose_name_plural = UI_feedback_to_news
        app_label = "backoffice"


class Comment(models.Model):
    """ Class COMMENT: rappresenta i commenti lasciati dagli utenti """

    news = models.ForeignKey(NewsItem, on_delete=models.PROTECT, null=True)
    user = models.ForeignKey(TelegramUser, on_delete=models.PROTECT, null=True)

    text = models.TextField(max_length=4096, verbose_name='commento')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = UI_comment_to_news
        verbose_name_plural = UI_comment_to_news_plural
        app_label = "backoffice"

    def __str__(self):
        return "Comment FOR " + \
               str(self.news) + " FROM " + \
               str(self.user)


class LogUserInteraction(models.Model):  # was CommandsFromUser
    # telegramUser = models.ForeignKey(TelegramUser, on_delete=models.PROTECT)
    user_id = models.BigIntegerField(verbose_name="telegram user id", default=-1)  # Telegram used id

    text = models.CharField(max_length=1024)

    # if true, command
    coming_from_user = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = UI_log_of_interactions_between_bot_and_users
        verbose_name_plural = UI_log_of_interactions_between_bot_and_users
        app_label = "backoffice"

    def __str__(self):
        return f"LogUserInteraction: user_id={self.user_id} coming_from_user={self.coming_from_user}  {self.created_at}  {self.text}"


# class UserActivityLog(models.Model):
#     user_id = models.BigIntegerField()
#     news_id = models.BigIntegerField()
#
#     value = models.CharField(max_length=1, blank=True, null=True)
#
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         app_label = "backoffice"


class SystemParameter(models.Model):
    name = models.CharField(max_length=256, blank=False)

    value = models.TextField(max_length=4096, blank=False)

    comment = models.CharField(max_length=256, blank=True, editable=False)

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

        SystemParameter.add_default_param(UI_PRIVACY, "http://www.regione.fvg.it/rafvg/cms/RAFVG/formazione-lavoro/lavoro/allegati/informativa_dir_lavoro_servizi_messaggistica102019.pdf", "regolamento della privacy")

        # SystemParameter.add_default_param(UI_select_news_categories, "Seleziona le categorie di news a cui sei interessato:")

        SystemParameter.add_default_param(UI_bot_presentation, "Benvenuto al bot Telegram della Direzione centrale lavoro, formazione, istruzione e famiglia - Regione Autonoma Friuli Venezia Giulia :)", "è mostrato nel comando /start")

        # SystemParameter.add_default_param("DEBUG_SEND_NEWS", "False", "non setta come processati le news item")

        SystemParameter.add_default_param(UI_bot_help_message, get_bot_default_help_msg(), "è mostrato nel comando /help")

        # SystemParameter.add_default_param(UI_request_for_news_item_feedback, "Ti è utile questa news?", "messaggio all'utente per chiedere feedback dopo aver ricevuto una news")

        # SystemParameter.add_default_param(param_show_match_category_news, "True", "mostra la categoria della news che ha permesso l'invio all'utente")

        SystemParameter.add_default_param(RSS_FEED, "http://www.regione.fvg.it/rafvg/cms/RAFVG/formazione-lavoro/servizi-lavoratori/news/?rss=y", "rss feed to watch")

        return True

    class Meta:
        verbose_name = UI_system_parameter
        verbose_name_plural = UI_system_parameters
        app_label = "backoffice"

    def __str__(self):
        return str(self.name)
