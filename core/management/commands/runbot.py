from django.core.management import BaseCommand
from core.factory import bot


class Command(BaseCommand):
    """
    Deletes the webhook and run the bot instance via long polling, at the end sets the webhook back.
    Only meant to be run locally to test the bot, not for production purposes.
    Webhook option must be used for production.
    """

    def handle(self, *args, **options):
        webhook = bot.get_webhook_info()
        print("Webhook:", webhook.url)
        bot.delete_webhook()
        try:
            print("Running the bot...")
            bot.polling(non_stop=True, skip_pending=True)
        except KeyboardInterrupt:
            print("\nStopping the bot & setting the webhook back...")
        except Exception:
            raise
        finally:
            bot.set_webhook(url=webhook.url)
        print("Done!")
