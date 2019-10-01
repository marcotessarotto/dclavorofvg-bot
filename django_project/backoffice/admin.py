from django.contrib import admin
from django.forms import (
    CheckboxSelectMultiple,
    TextInput
)

from .models import *


admin.site.site_header = 'backoffice GiovaniFVG'


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'user_id', 'regionefvg_id', 'is_bot')
    ordering = ('created_at',)
    list_filter = ('is_bot', )

    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},

        # https://stackoverflow.com/questions/910169/resize-fields-in-django-admin
        models.CharField: {'widget': TextInput(attrs={'size': '80'})},
        #        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},

    }


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('key', 'name')

    def add_default_categories(self, request):
    # def add_default_categories(self, request, queryset):
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
    list_display = ('news_id', 'title', 'created_at', 'like', 'dislike')
    exclude = ('like', 'dislike')


@admin.register(Comment)
class FeedbackOnNewsItemAdmin(admin.ModelAdmin):
    list_display = ('text', 'news', 'user')


admin.site.register(NewsFile)

