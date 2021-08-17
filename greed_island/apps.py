from django.apps import AppConfig


class GreedIslandConfig(AppConfig):
    name = 'greed_island'
    verbose_name = 'Greed Island'

    def ready(self):
        import greed_island.signals
