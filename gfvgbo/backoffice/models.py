

from django.db import models

from django.forms import CheckboxSelectMultiple

from django.forms import TextInput, Textarea

from django.contrib import admin

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


DEFAULT_KEYWORDS = []
DEFAULT_KEYWORDS_DICT = {}

def get_default_keywords_dict():
    return DEFAULT_KEYWORDS_DICT

def check_initial_keywords():
    from .definitions import get_categories_dict

    dict = get_categories_dict()

    my_list = []
    my_dict = {}

    for idx, val in dict.items():
        my_list.append((idx, val[0]))
        my_dict[idx] = val[0]

    # print(my_list)

    global DEFAULT_KEYWORDS
    DEFAULT_KEYWORDS = my_list

    global DEFAULT_KEYWORDS_DICT
    DEFAULT_KEYWORDS_DICT = my_dict

    pass


check_initial_keywords()


class Keyword(models.Model):

    key = models.CharField(max_length=2)
    #keyword = models.TextField(max_length=256, blank=True, choices=DEFAULT_KEYWORDS, default='-')

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "backoffice"

    def __str__(self):
        return "Keyword " + str(self.id) + ": " + str(self.key)  + " " + DEFAULT_KEYWORDS_DICT[self.key] + " "  + str(self.updated_at)


def fill_keywords():
    if len(Keyword.objects.all()) == 0:
        for i in DEFAULT_KEYWORDS:
            x = i[0]
            # y = i[1]
            k = Keyword()
            k.key = x

            k.save()


try:
    fill_keywords()
except Exception as e:
    logging.error(traceback.format_exc())
    # Logs the error appropriately.


def create_default_keywords_for_user(tuser):
    """

    :type tuser: TelegramUser
    """
    for k in Keyword.objects.all():
        tuser.keywords.add(k)
        k.save()

    tuser.save()


class TelegramUser(models.Model):
    # {'id': 884401291, 'first_name': 'Marco', 'is_bot': False, 'last_name': 'Tessarotto', 'language_code': 'en'}

    # {'id': 731571160, 'first_name': 'Matteo', 'is_bot': False, 'last_name': 'Merz', 'username': 'mttmerz', 'language_code': 'it'}
    user_id = models.BigIntegerField()

    giovanifvg_id = models.BigIntegerField(default=-1)

    username = models.TextField(max_length=256, blank=True, null=True)

    first_name = models.TextField(max_length=256, blank=True, null=True)
    last_name = models.TextField(max_length=256, blank=True, null=True)

    is_bot = models.BooleanField(default=False)

    language_code = models.CharField(max_length=2, blank=True, null=True)

    keywords = models.ManyToManyField(Keyword,   blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "TelegramUsers"
        app_label = "backoffice"

    def __str__(self):
        return "TelegramUser " + str(self.id) + ": " + str(self.user_id)  + " " + str(self.first_name) + " " + str(self.last_name) + " " + str(self.created_at)


class NewsItem(models.Model):

    title = models.TextField(max_length=4096, blank=True, null=True)
    text = models.TextField(max_length=4096, blank=True, null=True)

    # https://docs.djangoproject.com/en/2.2/ref/contrib/postgres/fields/#django.contrib.postgres.fields.ArrayField
    tags = ArrayField(models.CharField(max_length=200), blank=True)


    # https://docs.djangoproject.com/en/2.2/ref/models/fields/#django.db.models.FileField
    # file will be saved to MEDIA_ROOT/uploads/2015/01/30
    files = ArrayField(models.FileField(upload_to='uploads/%Y/%m/%d/'), blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "backoffice"

    def __str__(self):
        return "NewsItem " + str(self.id) + ": " + str(self.title)  + " " + str(self.tags)


# class FeedbackOnNewsItem(models.Model):


# mission_a_cui_risponde = models.ForeignKey(Mission, on_delete=models.PROTECT)


class CommandsFromUser(models.Model):
    telegramUser = models.ForeignKey(TelegramUser, on_delete=models.PROTECT)

    command = models.CharField(max_length=256)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "backoffice"


class MyModelAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},

        # https://stackoverflow.com/questions/910169/resize-fields-in-django-admin
        models.CharField: {'widget': TextInput(attrs={'size': '80'})},
        #        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},

    }


# TODO: add  Feedback on NewsItem