"""
For some random reasons I decided to implement Greed Island part of the bot instance separately from main one.
So, here we are going to write a new bot definition.
"""
import logging
import traceback
import uuid

from django.conf import settings
from django.db.models import Count
from telebot import types

from core import constants
from core.models import User
from greed_island.constants import bot, urify, strings, dog
from greed_island.models import Tag, Answer, Comment, Question
from greed_island.utils import notifications
from greed_island.utils.repositories import QuestionRepository, AnswerRepository, CommentRepository


@bot.message_handler(commands=[constants.COMMAND_TAGS])
def command_handler(message):
    """
    We handle special commands here
    :param message: Message instance
    :return: None
    """
    logging.info(f'Got command: {message.text}')
    # we do not handle commands in group
    if not message.chat.type == 'private':
        # users should use commands only in provate chat, if they use it in group, we just delete the message
        bot.delete_message(message.chat.id, message.message_id)
        return

    user, _ = User.objects.get_or_create(uid=message.from_user.id)
    command = message.text[1:]

    if command == constants.COMMAND_TAGS:
        try:
            # we show all available tags and then let user choose their favourite ones to subscribe
            tags = Tag.objects.annotate(
                subscribers_count=Count('subscribers')) \
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
    # we do not process private messages
    if message.chat.type == 'private':
        return

    uid = message.from_user.id
    cid = message.chat.id
    user, _ = User.objects.get_or_create(uid=uid)
    # we either use text or caption of a photo as an input text
    text = message.text or message.caption or None

    # so, first things first, we need to store question and answer. to do so, we should identify them.
    # thanks to myself, i already wrote necessary tools for that

    # let's see what our dog can do
    if dog.is_question(message):
        try:
            # we have a question
            # we need to extract tags
            tags, start_of_tag_line, end_of_tag_line = dog.collect_question_tags(message)

            # extract question text and clean it
            question_text = f'{text[:start_of_tag_line]}{text[end_of_tag_line:]}'.strip()
            # register new question
            QuestionRepository.register(question_text, user, message, tags)
        except:
            logging.error(f"Could not complete question registration: {traceback.format_exc()}")

    elif dog.is_answer(message):
        AnswerRepository.register(message, reply_to_message_id=message.reply_to_message.message_id)

    if text in strings.gi_accept_answer_commands:
        # so, someone replied to message with a text which is a command to approve answer.
        # we need to check if this was a reply to an answer
        answer = Answer.get(
            message_id=message.reply_to_message.message_id if message.reply_to_message else None)
        if answer:
            # it was an answer, now check if this is the author of question of that answer
            if answer.question.author == user:
                # sugoi, this IS an author of that question, let's approve it
                question_notifier = notifications.QuestionNotifier(
                    answer.question, urify=urify, strings=strings, bot=bot)
                # mark the answer as accepted
                answer.is_accepted = True
                answer.save()
                # send notification to that legendary user who answered correctly
                question_notifier.notify_about_approval(answer)

    # admin commands start here
    if message.reply_to_message and text.startswith(constants.ADMIN_CMD_HEADER) and bot.is_commander(cid, uid):
        cmd = message.text.replace(constants.ADMIN_CMD_HEADER, '', 1).strip()
        # we have a commander

        try:
            # mark message as question
            if cmd.startswith(constants.ADMIN_CMD_MARK_AS_QUESTION):
                # command can include tags for question
                tags = dog.collect_tags(message)
                # admin wants to mark the message as a question, we'll register it
                question_text = message.reply_to_message.text or message.reply_to_message.caption
                # register new question here
                question_author, _ = User.objects.get_or_create(uid=message.reply_to_message.from_user.id)
                question = QuestionRepository.register(
                    question_text, question_author, message.reply_to_message, tags, tag_author=user)
                notifier = notifications.QuestionNotifier(question, urify, strings, bot)
                notifier.notify_about_marking_as_question(tags, message)

                bot.delete_message(cid, message.message_id)

            # mark message as answer
            if cmd.startswith(constants.ADMIN_CMD_MARK_AS_ANSWER):
                # we should mark the message as an answer to question
                # we should find message id of the replied message.
                # since every reply is saved in Comment model, we can search it from there
                comment = Comment.get(message_id=message.reply_to_message.message_id)

                if comment:
                    # if comment exists, it means we can detect its replied message
                    AnswerRepository.register(message.reply_to_message, reply_to_message_id=comment.reply_to_message_id)
                    question = Question.get(message_id=comment.reply_to_message_id)
                    notifier = notifications.QuestionNotifier(question, urify, strings, bot)
                    notifier.notify_about_marking_as_answer(message)
                else:
                    # we could not find reply from our database, it is probably not stored
                    logging.info('Could not find comment from database')

                bot.delete_message(cid, message.message_id)

            # remove tag(s) from question
            if cmd.startswith(constants.ADMIN_CMD_REMOVE_QUESTION_TAG):
                # we have a request from admin to remove certain tag(s) from question
                # we extract all tags from message
                tags = dog.collect_tags(message)
                question = QuestionRepository.remove_tags(message_id=message.reply_to_message.message_id, tags=tags)
                notifier = notifications.QuestionNotifier(question, urify, strings, bot)
                notifier.notify_about_removing_tags(tags, message)

                bot.delete_message(cid, message.message_id)
        except:
            logging.error(traceback.format_exc())

    if message.reply_to_message:
        # this is a comment (a reply) to some other message, we just need to store it
        CommentRepository.register(message)
