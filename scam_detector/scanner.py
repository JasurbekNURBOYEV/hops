"""
Scans incoming group messages and reports likely scams to the board group.
Board members decide what to do with them; we never delete or restrict anything here.
"""
import logging
import traceback

import telebot
from django.conf import settings

from core import constants as core_constants
from core.models import WhitelistedMessage
from core.strings import Strings
from scam_detector import constants
from scam_detector.classifier import scam_probability


def _chat_identifier(chat: telebot.types.Chat) -> str:
    # public groups are linked by username, private supergroups by c/<id without -100>
    if chat.username:
        return chat.username
    chat_id = str(chat.id)
    return f"c/{chat_id[4:] if chat_id.startswith('-100') else chat_id[1:]}"


def scan_update(bot: telebot.TeleBot, update: telebot.types.Update) -> None:
    """
    Classifies the message (or edited message) in the update and reports it to the board group
    if its scam probability is above the threshold. Never raises.
    :param bot: TeleBot instance used to report
    :param update: incoming update
    :return: None
    """
    try:
        message = update.message or update.edited_message
        if not message or message.chat.type not in constants.SCANNED_CHAT_TYPES:
            return
        if message.chat.id == settings.BOARD_GROUP_ID:
            return
        text = message.text or message.caption
        if not text or WhitelistedMessage.is_whitelisted(text):
            return

        probability = scam_probability(text)
        if probability <= constants.SCAM_PROBABILITY_THRESHOLD:
            return

        logging.info(f'Potential scam ({probability:.2%}) in chat {message.chat.id}, message {message.message_id}')
        forwarded = bot.forward_message(settings.BOARD_GROUP_ID, message.chat.id, message.message_id)
        bot.send_message(
            settings.BOARD_GROUP_ID,
            constants.POTENTIAL_SCAM_REPORT.format(
                probability=probability,
                user_id=message.from_user.id,
                user_name=Strings.clean_html(message.from_user.first_name),
                chat_identifier=_chat_identifier(message.chat),
                message_id=message.message_id,
            ),
            parse_mode=core_constants.DEFAULT_PARSE_MODE,
            reply_to_message_id=forwarded.message_id,
        )
    except Exception:  # noqa
        # scanning must never break regular update processing
        logging.error(traceback.format_exc())
