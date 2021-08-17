from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver

from greed_island.factory import bot
from greed_island.models import Tag
from greed_island.utils.notifications import TagNotifier
from greed_island.utils.uris import URIfy


@receiver(pre_save, sender=Tag)
def tag_modified(sender, instance, *args, **kwargs):
    if instance.pk:
        # existing tag has just been modified
        # we notify its owner about change
        urify = URIfy(bot=bot)
        notifier = TagNotifier(instance, urify=urify, strings=bot.strings, bot=bot)
        notifier.tag_changed(Tag.get(pk=instance.pk).name)


@receiver(pre_delete, sender=Tag)
def tag_deleted(sender, instance, *args, **kwargs):
    # when tag is deleted, we notify its author (why? to insult? maybe...)
    urify = URIfy(bot=bot)
    notifier = TagNotifier(instance, urify=urify, strings=bot.strings, bot=bot)
    notifier.tag_removed()
