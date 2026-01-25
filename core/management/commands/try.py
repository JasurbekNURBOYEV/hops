from django.core.management import BaseCommand


class Command(BaseCommand):
    """
    Deletes the webhook and run the bot instance via long polling, at the end sets the webhook back.
    Only meant to be run locally to test the bot, not for production purposes.
    Webhook option must be used for production.
    """

    def handle(self, *args, **options):
        """Do tests here"""
        pass
