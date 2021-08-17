"""
Focus on making URLs
"""
from telebot import TeleBot


class URIfy(object):
    """
    We try to create URIs (maybe URLs, i don't really care, call whatever you want)
    """
    BASE_URL = "https://t.me"
    CHAT_ID = None
    CHAT_USERNAME = None
    CHAT_LINK = None

    def __init__(self, bot: TeleBot):
        self.bot = bot

    def get_chat_username(self, chat_id: int) -> str:
        """
        We only update username if chat id is different, otherwise we return cached username
        :param chat_id: ID of target chat
        :return: URL
        """
        if self.CHAT_ID != chat_id:
            self.CHAT_ID = chat_id
            chat_info = self.bot.get_chat(chat_id)
            if chat_info.username:
                self.CHAT_USERNAME = chat_info.username
            else:
                self.CHAT_USERNAME = chat_id
        return self.CHAT_USERNAME

    def get_chat_link(self, chat_id: int) -> str:
        """
        To generate chat link. We use caching here too: generate new link as long as the chat id is new.
        :param chat_id: ID of target chat
        :return: URL
        """
        if chat_id != self.CHAT_ID:
            self.CHAT_USERNAME = self.get_chat_username(chat_id)
            if isinstance(self.CHAT_USERNAME, int):
                if self.CHAT_USERNAME < 0:
                    self.CHAT_LINK = f'{self.BASE_URL}/c/{str(self.CHAT_USERNAME)[4:]}'
                else:
                    self.CHAT_LINK = f'{self.BASE_URL}/c/{self.CHAT_USERNAME}'
            else:
                self.CHAT_LINK = f'{self.BASE_URL}/{self.CHAT_USERNAME}'
        return self.CHAT_LINK

    def get_message_link(self, chat_id: int, message_id: int) -> str:
        """
        Make URL for message
        :param chat_id: ID of target chat
        :param message_id: ID of target message
        :return: URL to message in chat
        """
        return f'{self.get_chat_link(chat_id)}/{message_id}'

    def get_message_thread_link(self, chat_id: int, message_id: int) -> str:
        """
        We try to generate a link to open thread view of a single message.
        Thread view shows all replies to a message with a fancy design.
        Template: msg_link?thread=msg_id
        :param chat_id: ID of target chat
        :param message_id: ID of target message
        :return: URL
        """
        return f"{self.get_message_link(chat_id, message_id)}?thread={message_id}"
