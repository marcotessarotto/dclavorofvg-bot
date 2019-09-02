

from django.db import models

from django.forms import CheckboxSelectMultiple

from django.forms import TextInput, Textarea

from django.contrib import admin

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
    user_id = models.BigIntegerField()

    giovanifvg_id = models.BigIntegerField(default=-1)

    first_name = models.TextField(max_length=256, blank=True)
    last_name = models.TextField(max_length=256, blank=True)

    is_bot = models.BooleanField(default=False)

    language_code = models.CharField(max_length=2, blank=True)

    keywords = models.ManyToManyField(Keyword,   blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "TelegramUsers"
        app_label = "backoffice"

    def __str__(self):
        return "TelegramUser " + str(self.id) + ": " + str(self.user_id)  + " " + self.first_name + " " + self.last_name + " " + str(self.created_at)


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


