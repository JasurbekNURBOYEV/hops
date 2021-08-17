"""
For some random reasons I decided to implement Greed Island part of the bot instance separately from main one.
So, here we are going to write a new bot definition.
"""
import logging
import traceback
import uuid

from telebot import types

from django.conf import settings
from django.db.models import Count

from core import constants
from core.factory import HopsBot
from core.models import User
from core.strings import Strings
from greed_island.models import Question, Tag, Answer
from greed_island.utils import searchers, notifications
from greed_island.utils.uris import URIfy

# globals
bot = HopsBot(token=settings.BOT_TOKEN)
urify = URIfy(bot=bot)
strings = Strings()


@bot.message_handler(commands=[constants.COMMAND_TAGS])
def command_handler(message):
    """
    We handle special commands here
    :param message: Message instance
    :return: None
    """
    user, _ = User.objects.get_or_create(uid=message.from_user.id)
    command = message.text[1:]

    if command == constants.COMMAND_TAGS:
        try:
            # we show all available tags and then let user choose their favourite ones to subscribe
            tags = Tag.objects.annotate(
                subscribers_count=Count('subscribers'))\
                .values('name', 'subscribers_count').order_by('-subscribers_count')[:10]
            logging.info(f'TAGS: {tags}')
            tags_with_subscribers = []
            for tag in tags:
                tag_subs = tag['subscribers_count']
                if tag_subs:
                    tags_with_subscribers.append(f'{strings.gi_tag_format.format(tag=tag["name"])}({tag_subs})')
                else:
                    tags_with_subscribers.append(strings.gi_tag_format.format(tag=tag["name"]))
            tags_message = strings.gi_tags_list.format(
                tags_list=", ".join(tags_with_subscribers)
            )
            buttons = types.InlineKeyboardMarkup()

            if not user.uuid:
                # re-generates uuid
                user.uuid = uuid.uuid4()
                user.save()

            buttons.add(
                types.InlineKeyboardButton(
                    text=strings.gi_tag_dashboard_button_text,
                    url=f'{settings.DOMAIN_URL}/tags/{user.uuid.hex}/'
                )
            )
            bot.reply_to(message, text=tags_message, parse_mode=constants.DEFAULT_PARSE_MODE, reply_markup=buttons)
        except:
            logging.error(traceback.format_exc())


# ordinary text message handler
@bot.message_handler(content_types=['text', 'photo'])
def text_handler(message):
    """
    Listen, we have ultimate goal here: catch every possible question & answer
    and try to process them under certain rules. Rules may include (but not limited to):
     + store question
     + store answer
     + detect topic of question
     + make everything searchable (I mean, not something like a Google.
        Someone would have to pay me I did that, so, forget it)
     + build a suggestion system to suggest answers to already-asked questions (this is gonna be hard)
     + think about some other random stuff and try implementing...
    :param message: Message instance
    :return: None
    """
    user, _ = User.objects.get_or_create(uid=message.from_user.id)
    # we either use text or caption of a photo as an input text
    text = message.text or message.caption or None

    # so, first things first, we need to store question and answer. to do so, we should identify them.
    # thanks to myself, i already wrote necessary tools for that
    dog = searchers.Search()

    # let's see what our dog can do
    if dog.is_question(message):
        try:
            # we have a question
            # we need to extract tags
            tags, start_of_tag_line, end_of_tag_line = dog.collect_question_tags(message)
            logging.info(f'Tags: {", ".join(tags)}')

            # extract question text and clean it
            question_text = f'{text[:start_of_tag_line]}{text[end_of_tag_line:]}'.strip()

            # sometimes we might have devs playing with this feature: sends only tags and without an actual question
            # we don't allow "non-question" questions
            # if question text is empty -> skip it
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
                for tag in tags:
                    tag, _ = Tag.objects.get_or_create(name=tag, defaults=dict(author=user))
                    # register tags for the question
                    question.tags.add(tag)

                if new_question:
                    # alright, we have just saved the question
                    # now, we need to notify users who subscribed to specific tags
                    question_notifier = notifications.QuestionNotifier(question, urify=urify, strings=strings, bot=bot)
                    question_notifier.notify_subscribers()
                    # done
        except:
            logging.error(f"Could not complete question registration: {traceback.format_exc()}")

    elif dog.is_answer(message):
        # we have an answer, let's start by saving it
        question = Question.get(message_id=message.reply_to_message.message_id)
        if question:
            # replied message is not question or does not exist in our db, we skip/ignore this answer
            clean_answer = dog.clean_answer(message)
            Answer.objects.get_or_create(
                question=question, text=clean_answer, author=user, message_id=message.message_id,
                chat_id=message.chat.id,
                reply_to_message_id=message.reply_to_message.message_id if message.reply_to_message else None)
            bot.send_message(chat_id=user.uid,
                             text=urify.get_message_thread_link(
                                 chat_id=question.chat_id, message_id=question.message_id))

    if text in strings.gi_accept_answer_commands:
        # so, someone replied to message with a text which is a command to approve answer.
        # we need to check if this was a reply to an answer
        try:
            answer = Answer.get(
                message_id=message.reply_to_message.message_id if message.reply_to_message else None)
            if answer:
                # it was an answer, now check if this is the author of question of that answer
                if answer.question.author == user:
                    # sugoi, this IS an author of that question, let's approve it
                    question_notifier = notifications.QuestionNotifier(answer.question, urify=urify, strings=strings,
                                                                       bot=bot)
                    # mark the answer as accepted
                    answer.is_accepted = True
                    answer.save()
                    # send notification to that legendary user who answered correctly
                    logging.info('Notifying about answer approval...')
                    question_notifier.notify_about_approval(answer)
        except:
            logging.error(traceback.format_exc())
