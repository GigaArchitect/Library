from importlib import import_module
from django.contrib import admin
from django.apps import apps

# Register your models here.

app = apps.get_app_config("library_api")

for model in app.get_models():
    admin.site.register(model)
