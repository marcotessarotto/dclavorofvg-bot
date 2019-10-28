import os
import django
# init of django environment must be done before importing django models
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_settings")
django.setup()
