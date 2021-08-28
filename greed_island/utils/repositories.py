"""
We'll be using this file to simplify, generialize overall process of working with database.
We simply collect all repeated codebase and make functions/methods out of them.
After all, we don't like repeating ourselves.
"""
import traceback
from typing import Iterable

from telebot.types import Message

from core.models import User
from greed_island.constants import urify, strings, bot, dog
from greed_island.models import Question, Tag, Answer, Comment
from greed_island.utils import notifications
import logging


class BaseRepository(object):
    """
    Base abstract layer for further implementations
    """
    @staticmethod
    def register(*args, **kwargs):
        raise NotImplementedError()


class QuestionRepository(BaseRepository):
    """
    To work with Question model.
    """

    @staticmethod
    def register(question_text: str, user: User, message: Message, tags: Iterable[str],
                 tag_author: User = None) -> Question or None:
        """
        Used to register new question: save it to database, and do further processing (e.g: notifications)
        :param tag_author: author of tags, if None, author of question is taken
        :param question_text: clean question text
        :param user: user - author of question
        :param message: message instance of question
        :param tags: list of strings representing all tags of question
        :return: question instance
        """
        # sometimes we might have devs playing with this feature: sends only tags and without an actual question
        # we don't allow "non-question" questions
        # if question text is empty -> skip it
        logging.info(f'Question text: {question_text}')
        question = None
        if question_text:
            existing_instance = Question.objects.filter(text=question_text, author=user, chat_id=message.chat.id)
            new_question = True
            if not existing_instance.exists():
                question = Question.create(
                    text=question_text, author=user,
                    chat_id=message.chat.id,
                    message_id=message.message_id,
                    reply_to_message_id=message.reply_to_message.message_id if message.reply_to_message else None
                )
            else:
                new_question = False
                question = existing_instance.first()
            logging.info(f'Question: {question}')
            QuestionRepository.add_tags(tags, question=question, author=tag_author or question.author)

            if new_question:
                logging.info('New question, notifying...')
                # alright, we have just saved the question
                # now, we need to notify users who subscribed to specific tags
                question_notifier = notifications.QuestionNotifier(question, urify=urify, strings=strings, bot=bot)
                question_notifier.notify_subscribers()
                # done
            else:
                logging.info('Old question')
        return question

    @staticmethod
    def remove_tags(message_id: int, tags: Iterable[str]) -> Question or None:
        """
        Used to remove tags from existing question
        :param message_id: message id of question message
        :param tags: list of strings representing tags
        :return: question instance
        """
        question = Question.get(message_id=message_id)
        if question:
            for tag in tags:
                tag_instance = Tag.get(name=tag)
                if tag_instance:
                    question.tags.remove(tag_instance)
        return question

    @staticmethod
    def add_tags(tags: Iterable[str], question: Question = None, message_id: int = None,
                 author: User = None) -> Question or None:
        """
        Used to add tags to existing question
        :param author: author of tags, if None, author of question is taken
        :param question: question instance. at least question or message_id must be provided
        :param message_id: message if of question message
        :param tags: list of strings representing tags
        :return: question instance
        """
        if not any((message_id, question)):
            raise ValueError("Please, at least provide one of these: question, message_id")

        if message_id and not question:
            question = Question.get(message_id=message_id)

        if not question:
            # we tried but could not find question instance
            logging.error(f'Could not fin question with message_id={message_id}')
            return None

        logging.info('Registering the tags...')
        for tag in tags:
            tag_instance, _ = Tag.objects.get_or_create(name=tag, author=author or question.author)
            question.tags.add(tag_instance)

        return question


class AnswerRepository(BaseRepository):
    """
    To work with Answer model.
    """

    @staticmethod
    def register(message: Message, reply_to_message_id: int) -> Answer or None:
        """
        Used to register new answer: save it to db and do further processing if necessary
        :param reply_to_message_id: message id of the message which current message is replied to
        :param message: message instance of answer
        :return: answer instance
        """
        # we have an answer, let's start by saving it
        answer = None
        try:
            question = Question.get(message_id=reply_to_message_id)
            logging.info(f'Registering the answer for question: {question}')
            user, _ = User.objects.get_or_create(uid=message.from_user.id)
            logging.info(f'User: {user}')
            if question:
                # replied message is not question or does not exist in our db, we skip/ignore this answer
                clean_answer = dog.clean_answer(message)
                logging.info(f'Saving to db...')
                answer, _ = Answer.objects.get_or_create(
                    question=question, text=clean_answer, author=user, message_id=message.message_id,
                    chat_id=message.chat.id,
                    reply_to_message_id=reply_to_message_id)
        except:
            logging.error(traceback.format_exc())
        return answer


class CommentRepository(BaseRepository):
    """
    Here we work with Comment model, which is roughly used to store all reply messages.
    """

    @staticmethod
    def register(message: Message) -> Comment or None:
        """
        Used to register reply message: save it to db
        :return: comment instance
        """
        logging.info(f'Saving new comment...')
        text = message.text or message.caption
        user, _ = User.objects.get_or_create(uid=message.from_user.id)
        comment, _ = Comment.objects.get_or_create(
            chat_id=message.chat.id,
            message_id=message.message_id,
            reply_to_message_id=message.reply_to_message.message_id,
            text=text,
            author=user
        )
        return comment
