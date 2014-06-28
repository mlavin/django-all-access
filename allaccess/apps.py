try:
    from django.apps import AppConfig
except ImportError:
    AppConfig = object


class AllAccessConfig(AppConfig):
    name = 'allaccess'
