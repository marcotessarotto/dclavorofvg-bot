from django.contrib import admin
from django.forms import (
    CheckboxSelectMultiple,
    TextInput
)

import csv
from django.http import HttpResponse

from .models import *

try:
    from src.gfvgbo.secrets import BOT_NAME
except:
    from gfvgbo.secrets import BOT_NAME


admin.site.site_header = f'backoffice {BOT_NAME}'


# https://books.agiliq.com/projects/django-admin-cookbook/en/latest/export.html
class ExportCsvMixin:
    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"


class ExportAllTelegramUserData:
    def export_all_as_csv(self, request, queryset):

        # queryset = TelegramUser.objects.all()

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        categories = Category.objects.all().order_by('key')

        field_names_complete = field_names.copy()

        for cat in categories:
            field_names_complete.append(f"{cat.key} ({cat.name})")

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names_complete)

        try:
            education_level_pos = [i for i, x in enumerate(field_names) if x == "educational_level"][0]
        except IndexError:
            education_level_pos = None

        print(education_level_pos)

        for obj in queryset:

            row_values = [getattr(obj, field) for field in field_names]

            if education_level_pos:
                row_values[education_level_pos] = EDUCATIONAL_LEVELS[education_level_pos][1]

            for cat in categories:
                row_values.append("1" if cat in obj.categories.all() else "0")

            row = writer.writerow(row_values)

        return response

    export_all_as_csv.short_description = "Export user data with categories"


@admin.register(AiQAActivityLog)
class AiQAActivityLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'telegram_user', 'user_question', 'naive_sentence_similarity_action', 'naive_sentence_similarity_confidence', 'context')
    ordering = ('-id',)

    formfield_overrides = {
        # https://stackoverflow.com/questions/910169/resize-fields-in-django-admin
        models.CharField: {'widget': TextInput(attrs={'size': '80'})},
        #        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},

    }


@admin.register(NaiveSentenceSimilarityDb)
class NaiveSentenceSimilarityDbAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'reference_sentence', 'action', 'context', 'enabled', )
    ordering = ('-id', 'reference_sentence', 'action', 'context')
    search_fields = ('reference_sentence', 'action__action', 'context__context')
    actions = ["export_as_csv"]
    # TODO: add import csv command
    # https://books.agiliq.com/projects/django-admin-cookbook/en/latest/import.html

    formfield_overrides = {
        # https://stackoverflow.com/questions/910169/resize-fields-in-django-admin
        models.CharField: {'widget': TextInput(attrs={'size': '80'})},
        #        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},

    }


admin.site.register(AiContext)


@admin.register(AiAction)
class AiActionAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'action',)
    actions = ["export_as_csv"]
    ordering = ('-id', 'action')

    formfield_overrides = {
        # https://stackoverflow.com/questions/910169/resize-fields-in-django-admin
        models.CharField: {'widget': TextInput(attrs={'size': '80'})},
        #        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},

    }


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin, ExportAllTelegramUserData):
    list_display = ('username', 'first_name', 'last_name', 'user_id', 'is_admin', 'has_accepted_privacy_rules')
    ordering = ('id',)
    list_filter = ('has_accepted_privacy_rules', )
    search_fields = ('username', 'first_name', 'last_name', 'user_id')
    actions = ["export_all_as_csv"]

    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},

        # https://stackoverflow.com/questions/910169/resize-fields-in-django-admin
        models.CharField: {'widget': TextInput(attrs={'size': '80'})},
        #        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},

    }


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('key', 'name', 'emoji')
    ordering = ('key',)

    def add_default_categories(self, request):
        # fill_categories aggiunge le categorie di default soltanto se non ci sono Category
        result = Category.fill_categories()

        if result:
            self.message_user(request, "le categorie di default sono state aggiunte")
        else:
            self.message_user(request, "non ho fatto nulla, ci sono già categorie presenti")

        from django.http import HttpResponseRedirect
        return HttpResponseRedirect("../")

    add_default_categories.short_description = "Aggiungi le categorie di default"

    change_list_template = "categories/categories_changelist.html"

    actions = ["export_as_csv"]

    # https://books.agiliq.com/projects/django-admin-cookbook/en/latest/action_buttons.html
    def get_urls(self):
        urls = super().get_urls()
        from django.urls import path
        my_urls = [
            path('add_default_categories/', self.add_default_categories),
        ]
        return my_urls + urls


@admin.register(TextToSpeechWordSubstitution)
class TextToSpeechWordSubstitutionAdmin(admin.ModelAdmin):
    list_display = ('id', 'original', 'substitution', 'lang')


@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'title', 'list_of_categories', 'start_publication',  'processed', 'processed_timestamp', 'like', 'dislike', 'knowledge_base_article')
    exclude = ('like', 'dislike')
    search_fields = ('id', 'title')
    list_filter = ('categories',)
    actions = ["export_as_csv"]

    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},

        # https://stackoverflow.com/questions/910169/resize-fields-in-django-admin
        models.CharField: {'widget': TextInput(attrs={'size': '80'})},
        #        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},

    }

    def list_of_categories(self, obj):
        return ', '.join([a.name for a in obj.categories.all()])

    list_of_categories.short_description = "Categorie"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('text', 'news_id', 'user', 'created_at')
    # list_filter = ('news__id',)
    search_fields = ('news__id', 'user__user_id',)

    def news_id(self, obj):
        return "id=" + str(obj.news.id)


@admin.register(FeedbackToNewsItem)
class FeedbackToNewsItemAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('val', 'news_id', 'user', 'created_at')
    search_fields = ('news__id', 'user__user_id',)

    def news_id(self, obj):
        return "id=" + str(obj.news.id)


admin.site.register(NewsFile)


@admin.register(LogUserInteraction)
class CommandsFromUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'coming_from_user', 'created_at', 'text')
    search_fields = ('user_id', )


@admin.register(NewsItemSentToUser)
class NewsItemSentToUserAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('telegram_user', 'news_item', 'created_at',)
    search_fields = ('news_item__id', 'telegram_user__user_id',)
    actions = ["export_as_csv"]


@admin.register(UserFreeText)
class UserFreeTextAdmin(admin.ModelAdmin):
    list_display = ('telegram_user', 'created_at', 'text',)


@admin.register(MessageToUser)
class MessageToUserAdmin(admin.ModelAdmin):
    list_display = ('telegram_user', 'created_at', 'text',)


@admin.register(RssFeedItem)
class RssFeedItemAdmin(admin.ModelAdmin):
    list_display = ('data_feed_was_last_updated', 'category', 'processed', 'rss_title',)
    ordering = ('-updated_parsed',)
    list_filter = ('processed', )


@admin.register(CategoriesGroup)
class CategoriesGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'list_of_categories')

    def list_of_categories(self, obj):
        return ', '.join([a.name for a in obj.categories.all()])

    list_of_categories.short_description = "Categorie scelte"


@admin.register(SystemParameter)
class SystemParameterAdmin(admin.ModelAdmin):
    ordering = ('name',)

    def add_default_system_parameters(self, request):
        # fill_categories aggiunge le categorie di default soltanto se non ci sono Category
        result = SystemParameter.update_system_parameters()

        if result:
            self.message_user(request, "i parametri di sistema di default sono stati aggiornati")
        else:
            self.message_user(request, "non ho fatto nulla, ci sono già dei parametri di sistema ")

        from django.http import HttpResponseRedirect
        return HttpResponseRedirect("../")

    add_default_system_parameters.short_description = "Aggiungi li parametri di sistema di default"

    change_list_template = "system_parameters/syspar_custom_buttons.html"

    # https://books.agiliq.com/projects/django-admin-cookbook/en/latest/action_buttons.html
    def get_urls(self):
        urls = super().get_urls()
        from django.urls import path
        my_urls = [
            path('add_default_system_parameters/', self.add_default_system_parameters),
        ]
        return my_urls + urls