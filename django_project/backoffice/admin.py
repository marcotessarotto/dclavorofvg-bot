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


@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin):
    list_display = ('news_id', 'title', 'created_at', 'like', 'dislike')
    exclude = ('like', 'dislike')


@admin.register(Comment)
class FeedbackOnNewsItemAdmin(admin.ModelAdmin):
    list_display = ('text', 'news', 'user')

admin.site.register(NewsFile)

