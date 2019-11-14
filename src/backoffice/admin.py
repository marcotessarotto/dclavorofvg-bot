from django.contrib import admin
from django.forms import (
    CheckboxSelectMultiple,
    TextInput
)

from .models import *

admin.site.site_header = 'backoffice LavoroFVG'


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'user_id', 'is_admin', 'has_accepted_privacy_rules')
    ordering = ('id',)
    list_filter = ('has_accepted_privacy_rules', )
    search_fields = ('username', 'first_name', 'last_name', 'user_id')

    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},

        # https://stackoverflow.com/questions/910169/resize-fields-in-django-admin
        models.CharField: {'widget': TextInput(attrs={'size': '80'})},
        #        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},

    }


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
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

    # https://books.agiliq.com/projects/django-admin-cookbook/en/latest/action_buttons.html
    def get_urls(self):
        urls = super().get_urls()
        from django.urls import path
        my_urls = [
            path('add_default_categories/', self.add_default_categories),
        ]
        return my_urls + urls

    #actions = [add_default_categories]


@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at', 'list_of_categories', 'processed', 'processed_timestamp', 'like', 'dislike')
    exclude = ('like', 'dislike')
    search_fields = ('id', 'title')
    list_filter = ('categories',)

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
class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'news_id', 'user', 'created_at')
    # list_filter = ('news__id',)
    search_fields = ('news__id', 'user__user_id',)

    def news_id(self, obj):
        return "id=" + str(obj.news.id)


@admin.register(FeedbackToNewsItem)
class FeedbackToNewsItemAdmin(admin.ModelAdmin):
    list_display = ('val', 'news_id', 'user', 'created_at')
    search_fields = ('news__id', 'user__user_id',)

    def news_id(self, obj):
        return "id=" + str(obj.news.id)


admin.site.register(NewsFile)


@admin.register(CommandsFromUser)
class CommandsFromUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'coming_from_user', 'created_at', 'text')
    search_fields = ('user_id', )


@admin.register(NewsItemSentToUser)
class NewsItemSentToUserAdmin(admin.ModelAdmin):
    list_display = ('telegram_user', 'news_item', 'created_at',)
    search_fields = ('news_item__id', 'telegram_user__user_id',)


@admin.register(UserFreeText)
class UserFreeTextAdmin(admin.ModelAdmin):
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