from django.core.management import BaseCommand

from gfvgbo import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        # generate sql string to create database and user

        result = f"CREATE DATABASE {settings.DB_NAME} CHARACTER SET UTF8;\n" \
                 f"CREATE USER  {settings.DB_USERNAME}@localhost IDENTIFIED BY '{settings.DB_PWD}';\n" \
                 f"GRANT ALL PRIVILEGES ON {settings.DB_NAME}.* TO {settings.DB_USERNAME}@localhost;\n" \
                 f"FLUSH PRIVILEGES;\n"

        print(result)

        # print to stdout
        self.stdout.write(result)


