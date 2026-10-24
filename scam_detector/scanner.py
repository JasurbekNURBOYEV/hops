"""
Scans incoming group messages and reports likely scams to the board group.
Messages above the remove threshold are deleted right away; the rest are left to the board members,
who can delete them with the remove button on the report.
"""
import logging
import traceback
from typing import Optional

import telebot
from django.conf import settings

from core import constants as core_constants
from core.models import ScamMessage, WhitelistedMessage
from core.strings import Strings
from scam_detector import constants
from scam_detector.classifier import scam_probability


def _chat_identifier(chat: telebot.types.Chat) -> str:
    # public groups are linked by username, private supergroups by c/<id without -100>
    if chat.username:
        return chat.username
    chat_id = str(chat.id)
    return f"c/{chat_id[4:] if chat_id.startswith('-100') else chat_id[1:]}"


def _remove_markup(chat_id: int, message_id: int) -> telebot.types.InlineKeyboardMarkup:
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton(
            text=constants.REMOVE_BUTTON_TEXT,
            callback_data=constants.CALLBACK_DATA_REMOVE_TEMPLATE.format(chat_id=chat_id, message_id=message_id),
        )
    )
    return markup


def _parse_command(text: Optional[str], command: str) -> Optional[str]:
    """
    :param text: message text
    :param command: expected first line of the message
    :return: the text below the command (may be empty) if the message is that command, otherwise None
    """
    if not text:
        return None
    first_line, _, rest = text.partition('\n')
    if first_line.strip().lower() != command:
        return None
    return rest.strip()


def parse_scam_check(text: Optional[str]) -> Optional[str]:
    """
    :param text: message text
    :return: the text to score (may be empty) if the message is a !isscam command, otherwise None
    """
    return _parse_command(text, constants.SCAM_CHECK_COMMAND)


def parse_add_scam(text: Optional[str]) -> Optional[str]:
    """
    :param text: message text
    :return: the scam text to save (may be empty) if the message is an !addscam command, otherwise None
    """
    return _parse_command(text, constants.ADD_SCAM_COMMAND)


def reply_add_scam(bot: telebot.TeleBot, message: telebot.types.Message, scam_text: str) -> None:
    """
    Saves the scam text of an !addscam command and replies with the result.
    The caller is responsible for checking that the sender is allowed to add scam messages.
    :param bot: TeleBot instance used to reply
    :param message: the command message
    :param scam_text: text to save (from parse_add_scam)
    :return: None
    """
    if not scam_text:
        reply = constants.ADD_SCAM_USAGE
    elif ScamMessage.add(scam_text):
        logging.info(f'Scam message added by {message.from_user.id}')
        reply = constants.ADD_SCAM_ADDED
    else:
        reply = constants.ADD_SCAM_EXISTS
    bot.reply_to(message, reply, parse_mode=core_constants.DEFAULT_PARSE_MODE)


def reply_scam_check(bot: telebot.TeleBot, message: telebot.types.Message, candidate: str) -> None:
    """
    Scores the candidate text of a !isscam command and replies with the result.
    :param bot: TeleBot instance used to reply
    :param message: the command message
    :param candidate: text to score (from parse_scam_check)
    :return: None
    """
    if not candidate:
        bot.reply_to(message, constants.SCAM_CHECK_USAGE, parse_mode=core_constants.DEFAULT_PARSE_MODE)
        return
    probability = scam_probability(candidate)
    if probability > constants.SCAM_REMOVE_THRESHOLD:
        verdict = constants.SCAM_CHECK_VERDICT_SCAM
    elif probability > constants.SCAM_REPORT_THRESHOLD:
        verdict = constants.SCAM_CHECK_VERDICT_SUSPICIOUS
    else:
        verdict = constants.SCAM_CHECK_VERDICT_NOT_SCAM
    bot.reply_to(
        message,
        constants.SCAM_CHECK_RESULT.format(verdict=verdict, probability=probability),
        parse_mode=core_constants.DEFAULT_PARSE_MODE,
    )


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
        if parse_scam_check(message.text) is not None:
            # someone asked to score this text themselves, it is not their own message
            return
        if parse_add_scam(message.text) is not None and bot.is_commander(message.chat.id, message.from_user.id):
            # an admin is saving a scam sample, it is not their own message
            return

        probability = scam_probability(text)
        if probability <= constants.SCAM_REPORT_THRESHOLD:
            return

        logging.info(f'Potential scam ({probability:.2%}) in chat {message.chat.id}, message {message.message_id}')
        # forward before deleting, otherwise there is nothing left to show the board
        forwarded = bot.forward_message(settings.BOARD_GROUP_ID, message.chat.id, message.message_id)
        # our delete_message returns None (and logs) when deletion fails, e.g. the bot has no rights there
        removed = probability > constants.SCAM_REMOVE_THRESHOLD and bot.delete_message(
            message.chat.id, message.message_id)
        if removed:
            logging.info(f'Scam message {message.message_id} in chat {message.chat.id} removed automatically')
            ScamMessage.add(text)
        bot.send_message(
            settings.BOARD_GROUP_ID,
            constants.POTENTIAL_SCAM_REPORT.format(
                probability=probability,
                user_id=message.from_user.id,
                user_name=Strings.clean_html(message.from_user.first_name),
                chat_identifier=_chat_identifier(message.chat),
                message_id=message.message_id,
            ) + (constants.REMOVED_AUTOMATICALLY if removed else ''),
            parse_mode=core_constants.DEFAULT_PARSE_MODE,
            reply_to_message_id=forwarded.message_id,
            # removed messages need no decision, the rest are left to the board
            reply_markup=None if removed else _remove_markup(message.chat.id, message.message_id),
        )
    except Exception:  # noqa
        # scanning must never break regular update processing
        logging.error(traceback.format_exc())


def handle_remove_callback(bot: telebot.TeleBot, call: telebot.types.CallbackQuery, data: str) -> None:
    """
    Deletes the reported message from its group when a board member presses the remove button on the report.
    :param bot: TeleBot instance
    :param call: callback query of the remove button
    :param data: callback data without the header ("<chat_id>|<message_id>")
    :return: None
    """
    if call.message.chat.id != settings.BOARD_GROUP_ID:
        return
    chat_id, message_id = map(int, data.split(core_constants.CALLBACK_DATA_SEPARATOR))
    # our delete_message returns None (and logs) when deletion fails, e.g. the message is already gone
    deleted = bot.delete_message(chat_id, message_id)
    if not deleted:
        bot.answer_callback_query(call.id, text=constants.REMOVE_FAILED, show_alert=True)
        return
    logging.info(f'Scam message {message_id} in chat {chat_id} removed by {call.from_user.id}')
    # the report replies to the forwarded copy, which still has the text of the removed message
    forwarded = call.message.reply_to_message
    if forwarded:
        ScamMessage.add(forwarded.text or forwarded.caption)
    bot.edit_message_text(
        text=call.message.html_text + constants.REMOVED_BY.format(
            user_id=call.from_user.id,
            user_name=Strings.clean_html(call.from_user.first_name),
        ),
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode=core_constants.DEFAULT_PARSE_MODE,
    )
