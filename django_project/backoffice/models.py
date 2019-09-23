
from django.db import models

from django.contrib.postgres.fields import ArrayField

import traceback
import logging


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
    name = models.TextField(max_length=256)
    emoji = models.CharField(max_length=9, blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorie'
        app_label = 'backoffice'

    def __str__(self):
        return 'cat. ' + str(self.key) + ' (' +\
               str(self.name) + ')'


# Importa le categorie memorizzate nel file definitions.py
from .definitions import DEFAULT_CATEGORY_DICT


# Restituisce un dizionario delle categorie (quello appena importato)
def get_default_categories_dict():
    return DEFAULT_CATEGORY_DICT


# Popola la tabella Category (se vuota) con le categorie memorizzate nel dict
def fill_categories():
    if len(Category.objects.all()) == 0:
        for key in DEFAULT_CATEGORY_DICT:
            k = Category()

            k.key = key
            k.name = DEFAULT_CATEGORY_DICT[key][0]
            k.emoji = DEFAULT_CATEGORY_DICT[key][1]
            k.save()


try:
    fill_categories()
except Exception as e:
    logging.error(traceback.format_exc())
    # django.db.utils.ProgrammingError


# ****************************************************************************************
class TelegramUser(models.Model):
    """ Classe TELEGRAMUSER: rappresenta le informazioni legate agli utenti Telegram """

    user_id = models.BigIntegerField()

    regionefvg_id = models.BigIntegerField(default=-1) # for internal use

    has_accepted_privacy_rules = models.BooleanField(default=False)
    # L : through a parameter passed to /start
    # U : user must accept privacy rules
    privacy_acceptance_mechanism = models.CharField(max_length=1, blank=True, null=True)
    privacy_acceptance_timestamp = models.DateTimeField(blank=True, null=True)

    username = models.CharField(max_length=32, blank=True, null=True)

    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)

    is_bot = models.BooleanField(default=False)

    language_code = models.CharField(max_length=2, blank=True, null=True)

    categories = models.ManyToManyField(Category, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Utente Telegram"
        verbose_name_plural = "Utenti Telegram"
        app_label = "backoffice"

    def __str__(self):
        return 'user ' + str(self.user_id) + ' (' +\
               str(self.first_name) + ' ' + str(self.last_name) + ')'


# ****************************************************************************************

class NewsFile(models.Model):
    file_field = models.FileField(upload_to='uploads/%Y/%m/%d/')
    upload_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "backoffice"

    def __str__(self):
        return "" + str(self.id) + ": " + self.file_field.name + ", caricato il " + self.upload_date.strftime("%d/%m/%y")


class NewsItem(models.Model):
    """ Classe NEWSITEM: rappresenta le informazioni legati agli item di una news """

    news_id = models.CharField(max_length=5, blank=True, null=True)

    title = models.TextField(max_length=4096, blank=True, null=True)
    text = models.TextField(max_length=4096*4, blank=True, null=True)

    tags = ArrayField(
        models.CharField(max_length=200),
        blank=True,
        null=True,
        verbose_name="tags (separati da virgola)")

    link = models.TextField(max_length=4096, blank=True, null=True)

    # https://docs.djangoproject.com/en/2.2/ref/models/fields/#django.db.models.FileField
    # file will be saved to MEDIA_ROOT/uploads/2015/01/30
    #files = ArrayField(models.FileField(upload_to='uploads/%Y/%m/%d/'), blank=True, null=True)
    attached_files = models.ForeignKey(NewsFile, on_delete=models.PROTECT, null=True)

    like = models.BigIntegerField(default=0, editable=False)
    dislike = models.BigIntegerField(default=0, editable=False)

    start_publication = models.DateTimeField(blank=True, null=True)
    end_publication = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Articolo"
        verbose_name_plural = "Articoli"
        app_label = "backoffice"

    def __str__(self):
        return 'art. ' + str(self.news_id) + ' (' +\
               str(self.title) + ')'


# ****************************************************************************************
class Comment(models.Model):
    """ Class COMMENT: rappresenta i commenti lasciati dagli utenti """

    news = models.ForeignKey(NewsItem, on_delete=models.PROTECT, null=True)
    user = models.ForeignKey(TelegramUser, on_delete=models.PROTECT, null=True)

    text = models.TextField(max_length=1024, verbose_name='commento')

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


# TODO: add  Feedback on NewsItem
