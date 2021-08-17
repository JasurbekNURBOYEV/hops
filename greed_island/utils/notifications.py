"""
We'll be handling all notification stuff here.
We notify users when something special happens about questions, answers, tags
and basically anything related to Greed Island.
"""
import logging
import traceback

from telebot.apihelper import ApiTelegramException

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
        if not self.tag:
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
        if not self.tag:
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
