from django.contrib import admin
from .models import *


admin.site.site_header = 'backoffice GiovaniFVG'

admin.site.register(TelegramUser)
admin.site.register(CommandsFromUser)

