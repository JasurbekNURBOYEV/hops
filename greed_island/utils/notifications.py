"""
We'll be handling all notification stuff here.
We notify users when something special happens about questions, answers, tags
and basically anything related to Greed Island.
"""
import logging
import traceback
from typing import List

from telebot.apihelper import ApiTelegramException
from telebot.types import Message

from core import constants
from core.factory import HopsBot
from core.strings import Strings
from greed_island.models import Tag, Question, Answer
from greed_island.utils.uris import URIfy


class TagNotifier(object):
    """
    All notifications about Tags
    """

    def __init__(self, tag_pk_or_instance: int or Tag, urify: URIfy, strings: Strings, bot: HopsBot):
        if isinstance(tag_pk_or_instance, int):
            self.tag = Tag.get(pk=tag_pk_or_instance)
        elif isinstance(tag_pk_or_instance, Tag):
            self.tag = tag_pk_or_instance
        self.urify = urify
        self.strings = strings
        self.bot = bot

    def tag_changed(self, old_version: str) -> bool:
        """
        Our tags are automatically collected by user submissions. And sometimes we want to change/edit the tag in order
        to make it more proper. In that case we'll be notifying the author of the tag.
        :param old_version: previous version of Tag, used to show difference
        :return: bool indicating the status: True - notified, False - not notified
        """
        # check if Tag instance exists
        if not self.tag or not self.tag.author:
            # tag does not exist
            return False
        try:
            self.bot.send_message(
                chat_id=self.tag.author.uid,
                text=self.strings.gi_tag_changed_by_master.format(
                    old=self.strings.gi_tag_format.format(tag=old_version),
                    new=self.strings.gi_tag_format.format(tag=self.tag.name)
                ),
                parse_mode=constants.DEFAULT_PARSE_MODE
            )
        except ApiTelegramException as err:
            # we have a problem with sending the notification
            logging.error(f'Could not send notification about tag change. User: {self.tag.author}, tag: {self.tag}. '
                          f'Reason: {err}')
            return False

    def tag_removed(self) -> bool:
        """
        For some reasons tag may get deleted. We should notify author in that case.
        :return: bool indicating the status: True - notified, False - not notified
        """
        # check if Tag instance exists
        if not self.tag or not self.tag.author:
            # tag does not exist
            return False
        try:
            self.bot.send_message(
                chat_id=self.tag.author.uid,
                text=self.strings.gi_tag_removed_by_master.format(
                    tag=self.strings.gi_tag_format.format(tag=self.tag)
                ),
                parse_mode=constants.DEFAULT_PARSE_MODE
            )
        except ApiTelegramException as err:
            # we have a problem with sending the notification
            logging.error(f'Could not send notification about tag removal. User: {self.tag.author}, tag: {self.tag}. '
                          f'Reason: {err}')
            return False


class QuestionNotifier(object):
    """
    We include all notifications related to questions
    """

    def __init__(self, question_pk_or_instance: int or Question, urify: URIfy, strings: Strings, bot: HopsBot):
        if isinstance(question_pk_or_instance, int):
            self.question = Question.get(pk=question_pk_or_instance)
        elif isinstance(question_pk_or_instance, Question):
            self.question = question_pk_or_instance
        else:
            raise ValueError(f"question_pk_or_instance must be int or Question instance, "
                             f"found {type(question_pk_or_instance)}")
        self.urify = urify
        self.strings = strings
        self.bot = bot

    def notify_subscribers(self) -> bool:
        """
        When new question is received, we detect its tags and notify subscribers of those tags
        :return: bool indicating the status: True - notified, False - not notified
        """
        if not self.question:
            # question does not exist
            return False
        subscribers = {}
        for tag in self.question.tags.all():
            for subscriber in tag.subscribers.all():
                if subscriber.uid in subscribers:
                    subscribers[subscriber.uid].append(tag.name)
                else:
                    subscribers[subscriber.uid] = [tag.name]
        for uid, tags in subscribers.items():
            try:
                self.bot.send_message(
                    chat_id=uid,
                    text=self.strings.gi_new_question_received.format(
                        question=self.strings.clean_html(
                            self.strings.resize(self.question.text, max_size=127, ellipsis_at_end=True)),
                        tags=", ".join([self.strings.gi_tag_format.format(tag=tag) for tag in tags]),
                        link_to_message=self.urify.get_message_link(self.question.chat_id, self.question.message_id),
                        thread_link=self.urify.get_message_thread_link(self.question.chat_id, self.question.message_id)
                    ),
                    parse_mode=constants.DEFAULT_PARSE_MODE
                )
            except ApiTelegramException:
                # something bad happened
                logging.error("Could not notify tag subscribers:", traceback.format_exc())
        return True

    def notify_about_approval(self, answer_pk_instance: int or Answer) -> bool:
        """
        Send notification to author of answer: their answer has been accepted as correct solution
        :param answer_pk_instance: PK of Answer or its instance
        :return: bool indicating the status: True - notified, False - not notified
        """
        if isinstance(answer_pk_instance, int):
            answer = Answer.get(pk=answer_pk_instance)
        elif isinstance(answer_pk_instance, Answer):
            answer = answer_pk_instance
        else:
            raise ValueError(f"answer_pk_instance must be int or Answer instance, found {type(answer_pk_instance)}")

        try:
            self.bot.send_message(
                chat_id=answer.author.uid,
                text=self.strings.gi_answer_accepted_by_questioner.format(
                    link_to_answer_message=self.urify.get_message_link(answer.chat_id, answer.message_id)
                ),
                parse_mode=constants.DEFAULT_PARSE_MODE
            )
        except ApiTelegramException as a:
            # could not send the message
            logging.error('Could not send notification about answer approval:', a)
            return False
        except:
            logging.error('Unhandled exception on answer approval notifier:', traceback.format_exc())
        return True

    def notify_about_marking_as_question(self, tags: List[str], message: Message) -> bool:
        """
        When user forgets to use specific tag to mark the message as question, other superior users can mark
        it as question. When they do, we'll try to notify about this. This method is used to do that job.
        :param message: message instance of question
        :param tags: list of strings as tags, new tags can be added while marking the question
        :return: True - success, False - failure
        """

        # send message to admin
        try:
            removed_tags = self.strings.empty
            if tags:
                removed_tags = ', '.join([self.strings.gi_tag_format.format(tag=tag) for tag in tags])
            remaining_tags = self.strings.empty
            if self.question and self.question.tags.exists():
                remaining_tags = ', '.join([
                    self.strings.gi_tag_format.format(tag=tag.name) for tag in self.question.tags.all()])
            self.bot.send_message(
                message.from_user.id,
                text=self.strings.gi_marked_as_question.format(
                    msg_link=self.urify.get_message_link(message.chat.id, message.message_id),
                    new_tags=removed_tags,
                    all_tags=remaining_tags
                ),
                parse_mode=constants.DEFAULT_PARSE_MODE,
                disable_web_page_preview=True
            )
        except:
            logging.error(f'Could not send notification about marking as question: {traceback.format_exc()}')

        # send message to question's author in group
        try:
            self.bot.reply_to(
                message.reply_to_message,
                text=self.strings.gi_marked_as_question_to_author.format(
                    msg_link=self.urify.get_message_link(message.chat.id, message.reply_to_message.message_id)
                ),
                parse_mode=constants.DEFAULT_PARSE_MODE,
                disable_web_page_preview=True
            )
        except:
            logging.error(f'Could not send notification to question\'s author: {traceback.format_exc()}')
        return True

    def notify_about_removing_tags(self, tags: List[str], message: Message):
        """
        When some tags are removed from question, we notify people about it.
        :message: message instance
        :return: True - success, False - failure
        """
        try:
            removed_tags = self.strings.empty
            if tags:
                removed_tags = ', '.join([self.strings.gi_tag_format.format(tag=tag) for tag in tags])
            remaining_tags = self.strings.empty
            if self.question and self.question.tags.exists():
                remaining_tags = ', '.join([
                    self.strings.gi_tag_format.format(tag=tag.name) for tag in self.question.tags.all()])
            self.bot.reply_to(
                message.reply_to_message,
                text=self.strings.gi_tag_removed_from_question.format(
                    msg_link=self.urify.get_message_link(message.chat.id, message.reply_to_message.message_id),
                    removed_tags=removed_tags,
                    remaining_tags=remaining_tags
                ),
                parse_mode=constants.DEFAULT_PARSE_MODE,
                disable_web_page_preview=True
            )
            return True
        except:
            logging.error(f'Could not send notification about tag removal of question: {traceback.format_exc()}')
            return False

    def notify_about_marking_as_answer(self, message: Message) -> bool:
        """
        When admins mark message as answer, we notify necessary people about it.
        :message: message instance
        :return: True - success, False - failure
        """
        try:
            self.bot.reply_to(
                message.reply_to_message,
                text=self.strings.gi_marked_as_answer_to_author.format(
                    msg_link=self.urify.get_message_link(message.chat.id, message.message_id)),
                parse_mode=constants.DEFAULT_PARSE_MODE,
                disable_web_page_preview=True
            )
            return True
        except:
            logging.error(f'Could not send notification about marking as answer: {traceback.format_exc()}')
            return False
