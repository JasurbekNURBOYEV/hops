"""
This is a bot factory module which is roughly used to create full bot instance
"""
# --- START: IMPORTS
# built-in
from typing import List

# local
from service.core import models
from service.utils.decorators import lock_method_for_strangers

# django-specific
from django.conf import settings

# other/external
import telebot
# --- END: IMPORTS


class HopsBot(telebot.TeleBot):
    """
    An extended version of a TeleBot class.
    We'll be defining a bunch of custom behaviours here.
    """

    def is_member(self, uid: int, whitelist: List[int]) -> bool:
        """
        To check a membership os a user
        :param uid: user id
        :param whitelist: user ids to be considered as super users
        :return: boolean
        """
        assert isinstance(whitelist, list), "whitelist should a list object"
        if not whitelist:
            # if list is empty, we make a defualt one which includes the developer id
            whitelist = [settings.DEV_ID]
        member = None
        try:
            member = self.get_chat_member(settings.MAIN_GROUP_ID, uid)
        except telebot.apihelper.ApiTelegramException:
            try:
                member = self.get_chat_member(settings.TEST_GROUP_ID, uid)
            except telebot.apihelper.ApiTelegramException:
                pass
        finally:
            # we might get member, but status might be 'left'
            if member and member.status != 'left':
                return True
            elif uid in whitelist:
                # whitelist is a whitelist, we don't lock whitelisted users
                return True
            return False

    def notify_about_membership(self, message):
        self.send_message(message.from_user.id, "You have to be a member of main group")

    def welcome(self, message):
        chat_id = message.from_user.id
        uid = message.from_user.id
        instance = models.User.get(uid=uid)
        if not instance:
            # we have a new user
            bot.send_message(chat_id=chat_id, text="Hola")
        # TODO: complete this, because it is incomplete


# --- START: definition of bot instance
# initialize a bot instance
bot = HopsBot(token=settings.BOT_TOKEN)


# command handlers
@bot.message_handler(commands=['start'])
@lock_method_for_strangers(checker=bot.is_member, default=bot.notify_about_membership)
def start(message):
    text = message.text
    command = text[1:]

    # start command
    if command.startswith('start'):
        cmd = 'start'
        # check if it is a data-binded command
        data = command.replace(cmd, '', 1)
        if not data:
            # it is a pure command without additional data
            # we need to do tha basic start procedure
            bot.welcome(message)
        # TODO: complete the 'start command' body

# --- END: definition of bot instance
