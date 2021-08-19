from django.conf import settings

from core.factory import HopsBot
from core.strings import Strings
from greed_island.utils import searchers
from greed_island.utils.uris import URIfy

bot = HopsBot(token=settings.BOT_TOKEN)
urify = URIfy(bot=bot)
strings = Strings()
dog = searchers.Search()
