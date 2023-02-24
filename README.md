# dclavorofvg-bot
Telegram bot and backoffice for Direzione centrale lavoro, formazione, istruzione e famiglia, Regione Autonoma Friuli Venezia Giulia 


this project is being developed on Linux Debian 10

*project requirements:*

- python 3.11, mysqlclient
- Django 4.1.2
- python-telegram-bot 20

 
There are two main applications:

- Telegram bot (src/telegram_bot/regionefvg_bot.py)

- Django web application (i.e. start with 'python manage.py runserver' from directory django_project)


Before running the applications:

- create a database and a user in local mariadb instance
- create file src/gfvgbo/secrets.py containing:

DB_NAME="database name"

DB_USERNAME="database username"

DB_PWD="database password"

BOT_NAME = "Bot name"

MEDIA_ROOT = 'path on fs for storing media files'

NSS_HOST = 'hostname of nss server'

NSS_PORT = port number of nss server  

SOLR_HOST = 'hostname of apache solr instance'

SOLR_PORT = 8983

SECRET_KEY = "django secret"

SMTP_SERVER = ""

SMTP_USER = ""

SMTP_PASSWORD = ""

EMAIL_SENDER = "email address of sender"

SENTRY_SDK_CODE = "..."  # https://sentry.io SDK code, leave empty if not using it


- instruct Django to migrate applications and create superuser 
- get a token for you Telegram bot and save it in file token.txt positioned in the root of the project (src directory)
- start Django web app and the Telegram bot