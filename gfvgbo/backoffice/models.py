from django.db import models


class CustomDateTimeField(models.DateTimeField):
    def value_to_string(self, obj):
        val = self.value_from_object(obj)
        if val:
            val.replace(microsecond=0)
            return val.isoformat()
        return ''

class TelegramUser(models.Model):
    # {'id': 884401291, 'first_name': 'Marco', 'is_bot': False, 'last_name': 'Tessarotto', 'language_code': 'en'}
    user_id = models.BigIntegerField()
    first_name = models.TextField(max_length=256, blank=True)
    last_name = models.TextField(max_length=256, blank=True)

    is_bot = models.BooleanField(default=False)

    language_code = models.CharField(max_length=2, blank=True)

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


