from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # name = 'core.apps.app_auth'
    name = __name__.rsplit('.', 1)[0]
