from django.contrib import admin
from .models import *


admin.site.site_header = 'backoffice GiovaniFVG'

admin.site.register(TelegramUser, MyModelAdmin)
admin.site.register(CommandsFromUser)

admin.site.register(Keyword)

admin.site.register(NewsItem)