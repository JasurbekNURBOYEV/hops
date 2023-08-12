"""
This is a bot factory module which is roughly used to create full bot instance
"""
# --- START: IMPORTS
# built-in
import json
import base64
import random
from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Union
from random import shuffle
import logging
import traceback
import re
from io import BytesIO

# local
from core import models
from core import constants
from core.strings import Strings
from core.certificate import create_certificate
from utils.decorators import lock_method_for_strangers
from utils.piston import Interpreter

# django-specific
from django.core.files import File
from django.utils import timezone
from django.conf import settings
from django.db.models import Sum
from django.db.models import Q

# other/external
from telebot.types import Message
import telebot
from telebot import types
import pytesseract
from PIL import Image
import pytz

# --- END: IMPORTS


# --- START: GLOBALS
interpreter = Interpreter()


# --- END: GLOBALS


class HopsBot(telebot.TeleBot):
    """
    An extended version of a TeleBot class.
    We'll be defining a bunch of custom behaviours here.
    """
    strings = Strings()
    _id = _username = None

    @property
    def id(self):
        # we cache the bot id, since we may need it alot
        if self._id is None:
            self._id = self.get_me().id
        return self._id

    @property
    def username(self):
        if self._username is None:
            self._username = bot.get_me().username
        return self._username

    def set_context(self, message: telebot.types.Message, _key: str, _value) -> None:
        """
        Set values to main context
        :param message: Message instance
        :param _key: key
        :param _value: value
        :return: None
        """
        request_id = self.generate_unique_id(message=message)
        if hasattr(self, 'context'):
            self.context[request_id] = {_key: _value}

    @staticmethod
    def generate_unique_id(json_string: str = None, message: Message = None):
        """
        We use this to generate unique ID from either json or Message instance of a single message object.
        :param json_string: string of json
        :param message: Message instance
        :return: string representing a unique ID
        """
        template = '{date}-{chat_id}'
        if json_string:
            json_data = json.loads(json_string)
            msg = json_data[list(json_data.keys())[1]]
            return template.format(
                date=msg["date"], chat_id=msg["chat"]["id"])
        elif message:
            return template.format(date=message.date, chat_id=message.chat.id)
        else:
            raise ValueError("No data to process. Provide at least one of these: json_string, message")

    def is_member(self, uid: int, whitelist: List[int]) -> bool:
        """
        To check a membership os a user
        :param uid: user id
        :param whitelist: user ids to be considered as super users
        :return: boolean indicating the membership
        """
        assert isinstance(whitelist, list), "whitelist should a list object"
        if not whitelist:
            # if list is empty, we make a defualt one which includes the developer id
            whitelist = [settings.DEV_ID]
        member = None
        for chat in constants.ALLOWED_CHATS:
            try:
                member = self.get_chat_member(chat, uid)
            except telebot.apihelper.ApiTelegramException:
                pass
            if member and member.status != constants.USER_STATUS_LEFT:
                break
        # we might get member, but status might be 'left'
        if member and member.status != constants.USER_STATUS_LEFT:
            return True
        elif uid in whitelist:
            # whitelist is a whitelist, we don't lock whitelisted users
            return True
        return False

    def notify_about_membership(self, message) -> None:
        try:
            self.send_message(message.from_user.id, self.strings.you_are_not_a_member)
        except telebot.apihelper.ApiTelegramException:
            pass
        finally:
            # if user is not a member, using the bot is considered violation
            self.set_context(message, 'violation', True)

    @staticmethod
    def set_next_step(user: models.User, step: int, temp_data: str = None) -> None:
        """
        Just to save current step of user
        :param user: user instance
        :param step: int representing the current step
        :param temp_data: temporary data refers to string data which can be used to store some little data for steps
        :return: none
        """
        user.step = step
        user.temp_data = temp_data if temp_data is not None else user.temp_data
        user.save()

    def generate_quiz(
            self,
            message,
            index: int = 0,
            current_score: int = 0
    ) -> (models.Quiz, telebot.types.InlineKeyboardMarkup, str):
        """
        To generate a whole representable quiz
        :param current_score: current score tracker
        :param message: message object
        :param index: index of quiz
        :return: tuple including quiz instance, markup and a message string
        """
        uid = message.from_user.id
        quizzes = models.Quiz.all()
        if not quizzes.exists() or quizzes.count() <= index:
            # for some reasons we don't have quizzes (or at least a quiz for that index)
            return None, None, None
        quiz = quizzes[index]
        # create proper markup
        markup = types.InlineKeyboardMarkup(row_width=1)
        option_instances = list(models.QuizOption.filter(quiz=quiz))
        # we need to shuffle options a little bit
        shuffle(option_instances)
        # add each option to markup as inline keyboard
        for option in option_instances:
            markup.add(
                types.InlineKeyboardButton(
                    text=option.text,
                    callback_data=constants.CALLBACK_DATA_TEST_TEMPLATE.format(
                        uid=uid,
                        quiz_id=quiz.pk,
                        index=index,
                        option_id=option.pk,
                        current_score=current_score
                    )
                )
            )
        # create message string
        text = self.strings.test_question_template.format(
            index=index,
            question=quiz.question
        )
        # all done
        return quiz, markup, text

    def detect_prohibited_topic(self, text: str) -> List[Tuple[dict, List[str]]]:
        """
        This method is used to detect/collect prohibited topics/keywords
        :param text: message text
        :return: collection of detected keywords
        """
        text = text.lower()
        topics = settings.PROHIBITED_TOPICS
        detected_topics = []
        for topic in topics:
            detected_targets = []
            topic_name = topic['name']
            whitelist = topic.get('whitelist', [])
            targets = topic.get('targets', [topic_name])
            spoilers = topic.get('spoilers', [])
            clean_text = self.strings.clean_text(text, spoilers=spoilers)
            # let's analyze the text
            # try to connect all letters of target words together (if they are separated by spaces)
            # and collect all those suspicious words
            suspicious_words = set()
            for target_word in targets:
                s = "{1,}\s*"
                lets = "[a-z0-9]*"
                pattern = f"{lets}{target_word[0]}{s}{s.join([i for i in target_word[1:-1]])}{s}{target_word[-1]}{lets}"
                for i in re.findall(pattern, clean_text):
                    i = i.replace(' ', '')
                    final_word = ""
                    # remove repeated chars in one place
                    for j in range(1, len(i)):
                        if i[j] != i[j - 1]:
                            final_word += i[j - 1]
                    final_word += i[-1]
                    suspicious_words.add(final_word)
            # check every word against target word
            for word in suspicious_words:
                for target in targets:
                    if target in word:
                        for white in whitelist:
                            if white in word:
                                break
                        else:
                            detected_targets.append(word)
            if detected_targets:
                detected_topics.append((topic, detected_targets))
        return detected_topics

    def restrict_with_warning(self, message, detected_topics, user, reason: str = None):
        """
        To restrict users when prohibited topic is detected
        :param reason: custom reason by admin
        :param user: User object
        :param message: message
        :param detected_topics: list of detected topics
        :return: None
        """
        logging.warning(f"CHAT {message.chat.id=}")
        restriction_logs = models.Restriction.filter(user=user)
        overall_seconds = restriction_logs.aggregate(Sum('seconds')).get('seconds__sum')
        overall_seconds = overall_seconds if overall_seconds is not None else 0
        recent_log = restriction_logs.last()
        if recent_log:
            last_restriction_seconds = recent_log.seconds
        else:
            last_restriction_seconds = 0
        next_restriction_seconds = last_restriction_seconds + constants.DEFUALT_RESTRICTION_SECONDS
        until_date = datetime.now().replace(tzinfo=timezone.get_current_timezone()) + timedelta(
            seconds=next_restriction_seconds)
        try:
            topics = "\n".join(
                [
                    self.strings.prohibited_topic_template.format(
                        topic_name=topic['name'], words=', '.join(words), hint=topic.get('hint', '')
                    )
                    for topic, words in detected_topics
                ]
            )
            if reason:
                topics = reason
            if reason and len(reason.split()) == 1:
                tip = models.Tip.get(key=reason.lower())
                if tip and len(tip.message) <= constants.TIP_AS_TOPIC_PREVIEW_HINT_MAX_SIZE:
                    topics = self.strings.prohibited_topic_with_tip_template.format(
                        tip=tip.key,
                        description=tip.message,
                    )
            warning_message = self.strings.prohibited_topic_detected.format(
                topics=topics,
                user_name=self.strings.clean_html(message.from_user.first_name),
                user_id=message.from_user.id,
                date=(until_date.replace(tzinfo=pytz.UTC)).strftime("%Y-%m-%d %H:%M")
            )
            if overall_seconds >= constants.DEFAULT_BAN_LIMIT_SECONDS:
                # we need to ban the user
                self.kick_chat_member(message.chat.id, message.from_user.id)
            # try to delete message
            bot.delete_message(message.chat.id, message.message_id)
            # we try to restrict the user
            self.restrict_chat_member(
                message.chat.id,
                message.from_user.id,
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False,
                can_invite_users=False,
                until_date=int(until_date.timestamp())
            )
            msg = self.send_message(message.chat.id, warning_message, parse_mode=constants.DEFAULT_PARSE_MODE)
            # create restriction log
            models.Restriction.create(user=user, seconds=next_restriction_seconds,
                                      restriction_message_id=msg.message_id)
            
            # done
        except telebot.apihelper.ApiTelegramException as e:
            # we couldn't restrict, bot might not be an admin or some kind of fatal error occured
            logging.error(e)
        except Exception as fe:
            logging.error(fe)

        # set red flag to inform GI about violation
        self.set_context(message, 'violation', True)

    @staticmethod
    def get_daily_limit(user: models.User) -> int:
        """
        Returns daily limit for a user to run code in group
        :param user:
        :return:
        """
        certificate = models.Certificate.filter(user=user).last()
        if certificate:
            for name, percentage, limit in constants.TEST_CLASSES_BY_RESULT:
                if certificate.percentage / 100 >= percentage:
                    return limit
        return 0

    def get_remaining_limit(self, user: models.User) -> int:
        """
        Returns remaining limit for user to run code in group
        :param user:
        :return:
        """
        today = timezone.now()
        start_of_the_day = datetime(today.year, today.month, today.day)
        recent_codes = models.Code.filter(user=user, created_time__gte=start_of_the_day).filter(~Q(chat_id=user.uid))
        daily_limit = self.get_daily_limit(user)
        return daily_limit - recent_codes.count()

    def can_run_code(self, message) -> bool:
        """
        Detects whether user can run code or not
        :return:
        """
        user = models.User.get(uid=message.from_user.id)
        user_status = self.get_chat_member(message.chat.id, message.from_user.id).status
        if user_status in (constants.USER_STATUS_ADMIN, constants.USER_STATUS_OWNER):
            return True
        elif user and self.get_remaining_limit(user) >= 1:
            return True
        return False

    def should_check_for_prohibited_topic(self, message) -> bool:
        """
        Detects if the message should be analyzed for prohibited topics.
        We don't do it if chat is private or user is admin or owner
        :param message:
        :return:
        """
        user_info = self.get_chat_member(message.chat.id, message.from_user.id)
        if user_info and user_info.status in (constants.USER_STATUS_ADMIN, constants.USER_STATUS_OWNER):
            return False
        return message.chat.type != 'private'

    def is_commander(self, cid, uid) -> bool:
        """
        We can detect here if user can use admin commands or not
        :param cid:
        :param uid:
        :return:
        """
        user_info = self.get_chat_member(cid, uid)
        if user_info and user_info.status in (constants.USER_STATUS_ADMIN, constants.USER_STATUS_OWNER):
            return True
        elif uid == settings.DEV_ID:
            return True
        return False

    def send_message(
        self, chat_id: Union[int, str], text: str,
        parse_mode: Optional[str] = None,
        entities: Optional[List[types.MessageEntity]] = None,
        disable_web_page_preview: Optional[bool] = None,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: Optional[bool] = None,
        reply_markup: Optional[List] = None,
        timeout: Optional[int] = None,
    ) -> Optional[types.Message]:
        """
        The silent version of the original send_message.
        It is silent because it doesn't raise exceptions (at least this was what I thought).

        :return: Message on success, otherwise None.
        """
        try:
            return super().send_message(
                text=text,
                chat_id=chat_id,
                parse_mode=parse_mode,
                entities=entities,
                disable_web_page_preview=disable_web_page_preview,
                disable_notification=disable_notification,
                protect_content=protect_content,
                reply_to_message_id=reply_to_message_id,
                allow_sending_without_reply=allow_sending_without_reply,
                reply_markup=reply_markup,
                timeout=timeout
            )
        except:  # noqa
            logging.error("Error occurred while trying to send a message", exc_info=True)
            return None


# --- START: definition of bot instance
# initialize a bot instance
bot = HopsBot(token=settings.BOT_TOKEN)


# command handlers
@bot.message_handler(commands=[constants.COMMAND_START, constants.COMMAND_CANCEL, constants.COMMAND_TEST])
@lock_method_for_strangers(checker=bot.is_member, default=bot.notify_about_membership)
def command_handler(message):
    try:
        if not message.chat.type == 'private':
            # users should use commands only in provate chat, if they use it in group, we just delete the message
            bot.delete_message(message.chat.id, message.message_id)
            return

        text = message.text
        command = text[1:]
        uid = message.from_user.id
        user, _ = models.User.objects.get_or_create(uid=uid)

        # start command
        if command.startswith(constants.COMMAND_START) and message.chat.type == 'private':
            # check if it is a data-binded command
            try:
                data = command.replace(f"{constants.COMMAND_START} ", '', 1)
                if not data or data == constants.COMMAND_START:
                    # it is a pure command without additional data
                    # we need to do tha basic start procedure
                    bot.reply_to(message, bot.strings.welcome)
                else:
                    # we have data which needs processing
                    if data == constants.CMD_DATA_START_TEST:
                        # register the step & start
                        bot.set_next_step(user, constants.STEP_TEST_WAITING_TO_START)
                        bot.send_message(uid, text=bot.strings.start_test.format(count=models.Quiz.all().count()))
                        # hopefully we're done here
                    elif data.split(constants.CALLBACK_DATA_HEADER_SEPARATOR)[0] == constants.CMD_DATA_RULES:
                        chat_id = data.split(constants.CALLBACK_DATA_HEADER_SEPARATOR)[1]
                        # new user is requesting for rules
                        if user.agreement_time is not None:
                            # already agreed
                            bot.send_message(
                                uid, bot.strings.new_member_already_agreed, parse_mode=constants.DEFAULT_PARSE_MODE)
                        else:
                            bot.send_message(
                                uid,
                                bot.strings.new_member_rules.format(key=user.magic_word),
                                parse_mode=constants.DEFAULT_PARSE_MODE
                            )
                            bot.set_next_step(user, constants.STEP_AGREEMENT_WAITING_FOR_CONFIRMATION, chat_id)
                            # done
            except:  # noqa
                logging.error(traceback.format_exc())

        # cancel command
        elif command.startswith(constants.COMMAND_CANCEL) and message.chat.type == 'private':
            # this is where we handle cancellations
            # in any case, we just cancel whatever we were doing
            # and just head back to initial state
            bot.set_next_step(user=user, step=constants.STEP_INITIAL_POINT)
            bot.send_message(uid, bot.strings.cancelled)

        # test command - to start quiz
        elif command.startswith(constants.COMMAND_TEST) and message.chat.type == 'private':
            # register the step & start
            bot.set_next_step(user, constants.STEP_TEST_WAITING_TO_START)
            quizzes_count = models.Quiz.all().count()
            bot.send_message(uid, text=bot.strings.start_test.format(count=quizzes_count))
    except:  # noqa
        logging.error(f'Fatal error in command handler: {traceback.format_exc()}')


# new chat members handler
@bot.message_handler(content_types=['new_chat_member', 'new_chat_members'])
@lock_method_for_strangers(checker=bot.is_member, default=bot.notify_about_membership)
def new_chat_member_handler(message):
    # we handle new users joining our group here
    # we may have different scenarios:
    # - just a new user joined
    # - old user joined, but s/he didn't agree on our rules last time
    # - old user joined, s/he already agreed on rules
    # - old user joined, s/he was restricted, thus should wait until restriction expires

    # having all scenarios taken into consideration, we start the implementation one by one
    # let's check our guests
    for guest in message.new_chat_members:
        pattern_matched = False
        for pattern in settings.NEW_MEMBERS_TO_KICK_PATTERNS:
            if pattern(guest):
                bot.kick_chat_member(message.chat.id, guest.id)
                bot.send_message(settings.DEV_ID, f"User kicked on entrance: {guest.first_name}")
                pattern_matched = True
        if pattern_matched:
            continue
        # if our bot is added to a group, we check if it is allowed group
        if guest.id == bot.id:
            if message.chat.id not in constants.ALLOWED_CHATS:
                # this group is not allowed, so we are gonna leave
                bot.leave_chat(message.chat.id)
        # detecting and removing bots from group
        # start monarchy
        elif guest.is_bot:
            bot.kick_chat_member(message.chat.id, guest.id)
        # end monarchy
        elif not guest.is_bot:
            # we have new member in our allowed chat
            # our guest may have a very unpleasant nickname
            # we are going to normalize it
            guest_name = guest.first_name
            if guest.last_name:
                guest_name = " ".join((guest_name, guest.last_name))
            guest_name = bot.strings.resize(guest_name, 20)
            guest_name = bot.strings.clean_html(guest_name)
            # we choose a key for each guest, they will have to find the key in order get access to write
            key = random.choice(bot.strings.keys)
            # prepare callback buttons for our guest
            callback_data = constants.CALLBACK_DATA_NEW_MEMBER_TEMPLATE.format(
                uid=guest.id,
                chat_id=message.chat.id
            )
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton(
                    text=bot.strings.new_member_button_text,
                    callback_data=callback_data
                )
            )
            user, new = models.User.objects.get_or_create(uid=guest.id)
            # scenario 1: user is totally new
            if new:
                # try to restrict
                try:
                    bot.restrict_chat_member(
                        message.chat.id, guest.id,
                        can_send_messages=False,
                        can_send_media_messages=False,
                        can_send_other_messages=False,
                        can_add_web_page_previews=False,
                        can_invite_users=False
                    )
                    # restricted, now send a 'welcome' message
                    welcome_message = bot.send_message(
                        message.chat.id,
                        bot.strings.new_member.format(name=guest_name, uid=guest.id),
                        reply_markup=markup,
                        parse_mode=constants.DEFAULT_PARSE_MODE
                    )
                    # we save message id, so that we can delete or edit it when user agrees to rules
                    user.magic_word = key
                    user.welcome_message_id = welcome_message.message_id
                except telebot.apihelper.ApiTelegramException:
                    # we probably could not restrict the user due to lack of admin rights
                    logging.error(traceback.format_exc())
                except:  # noqa
                    # fatal error occurred
                    logging.error(traceback.format_exc())
            else:
                # since user is not new user, we may have old warning message
                # we need to delete it
                if user.welcome_message_id:
                    try:
                        bot.delete_message(message.chat.id, user.welcome_message_id)
                    except:  # noqa
                        # if we can't, we can't
                        pass
                # scenario 2: user is old, and already agreed on rules
                if user.agreement_time is not None:
                    guest_info = bot.get_chat_member(message.chat.id, guest.id)
                    # this scenario includes other two different scenarios
                    # 1 - user is currently restricted
                    # (was recently punished for some reason and now is trying to re-join)
                    # 2 - user is not restricted
                    if not guest_info.can_send_messages and guest_info.until_date:
                        until_date = datetime.fromtimestamp(guest_info.until_date).replace(
                            tzinfo=timezone.get_current_timezone())
                        # convert the time into human-readable string
                        representable_until_date = until_date.strftime(
                            bot.strings.restricted_until_time.format(
                                day=until_date.day,
                                month=bot.strings.month_to_str(until_date.month)
                            )
                        )
                        # we warn the user
                        bot.send_message(
                            message.chat.id,
                            bot.strings.new_member_already_restricted.format(
                                uid=guest.id,
                                name=guest_name,
                                time=representable_until_date
                            ),
                            parse_mode=constants.DEFAULT_PARSE_MODE
                        )
                    else:
                        # our old comrade has finally come back, let's give a hug
                        bot.send_message(
                            message.chat.id, bot.strings.new_member_old_comrade_back.format(
                                uid=guest.id, name=guest_name
                            ),
                            parse_mode=constants.DEFAULT_PARSE_MODE
                        )

                # scenario 3: user id old, but didn't agree on rules
                else:
                    # user hasn't agreed to rules yet
                    # let's remind
                    bot.restrict_chat_member(
                        message.chat.id, guest.id,
                        can_send_messages=False,
                        can_send_media_messages=False,
                        can_send_other_messages=False,
                        can_add_web_page_previews=False,
                        can_invite_users=False
                    )
                    welcome_message = bot.send_message(
                        message.chat.id,
                        bot.strings.new_member_not_agreed_yet.format(
                            uid=guest.id,
                            name=guest_name
                        ),
                        reply_markup=markup,
                        parse_mode=constants.DEFAULT_PARSE_MODE
                    )
                    user.welcome_message_id = welcome_message.message_id
            user.magic_word = key
            user.save()
    # try to delete service message
    bot.delete_message(message.chat.id, message.message_id)


# here we try to handle text messages
@bot.message_handler(content_types=['text'])
@lock_method_for_strangers(checker=bot.is_member, default=bot.notify_about_membership)
def text_handler(message):
    uid = message.from_user.id
    cid = message.chat.id
    text = message.text
    user, new = models.User.objects.get_or_create(uid=uid)
    # what we do here is basically working with steps
    # we do whatever necessary according the current state of the user
    # so, let's start by checking steps
    should_check_for_prohibited_topics = bot.should_check_for_prohibited_topic(message)
    if message.chat.type == 'private':
        # private chat is processed separately
        if user.step == constants.STEP_TEST_WAITING_TO_START:
            # if user is waiting for test to begin, that means now s/he sent us a full name
            # names are (and should be) built by only alpha chars
            if len(text.split()) == 2:
                # save full name to temp data (so that we can put it on certificate after finishing the test)
                user.temp_data = text
                user.save()
                # generate quiz and start testing
                quiz, markup, message_string = bot.generate_quiz(message)
                if not quiz:
                    # hmm, it seems we don't have quizzes yet
                    bot.send_message(uid, bot.strings.test_quizzes_not_found, parse_mode=constants.DEFAULT_PARSE_MODE)
                    bot.set_next_step(user, constants.STEP_INITIAL_POINT)
                    # yeah, we pretty much disappointed the user
                else:
                    # everything is ok
                    # let's start testing
                    # whoever you are, i'm not gonna forgive if you send the question to main group
                    bot.send_message(uid, text=message_string, reply_markup=markup,
                                     parse_mode=constants.DEFAULT_PARSE_MODE)
                    bot.set_next_step(user, constants.STEP_TEST_ONGOING)
            else:
                # that freaking user lied to us, this is definitely not his/her name
                # it has to be two words, one for name another for surname
                bot.send_message(uid, bot.strings.test_full_name_invalid)
        elif user.step == constants.STEP_AGREEMENT_WAITING_FOR_CONFIRMATION:
            # new user has sent key as a confirmation (for rules)
            if text.lower() == user.magic_word:
                # it is true, let's send a warm welcome message to our new comrade
                # first of all, we lift all restrictions
                chat_id = int(user.temp_data)
                try:
                    bot.restrict_chat_member(
                        chat_id, uid,
                        can_send_messages=True,
                        can_send_media_messages=True,
                        can_send_other_messages=True,
                        can_add_web_page_previews=True,
                        can_invite_users=True,
                    )
                    # edit welcome message
                    new_member_name = message.from_user.first_name
                    if message.from_user.last_name:
                        new_member_name = " ".join([new_member_name, message.from_user.last_name])
                    new_member_name = bot.strings.resize(new_member_name, 20)
                    new_member_name = bot.strings.clean_html(new_member_name)
                    bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=user.welcome_message_id,
                        text=bot.strings.new_member_welcome.format(uid=uid, name=new_member_name),
                        parse_mode=constants.DEFAULT_PARSE_MODE
                    )
                    bot.send_message(uid, bot.strings.new_member_congrats)
                    user.agreement_time = timezone.now()
                    user.save()
                    bot.set_next_step(user, constants.STEP_INITIAL_POINT)
                except telebot.apihelper.ApiTelegramException:
                    # probably we couldn't complete the task because bot has no enough admin rights
                    logging.error(traceback.format_exc())
            else:
                # wrong key
                bot.send_message(uid, bot.strings.new_member_wrong_key)

    # this is our main group chat (or other group chat)
    # what can we do in group:
    # + detect prohibited topics
    # + run code
    # + handle management commands
    # + what else?..

    # let's start with management commands
    # - admins alert: user can alert all admins at once by using special keyword
    # - tips: users can reply to messages and send useful tips to other users (e.g: this is offtopic, offtopic means...)
    # - ..?

    # admins alert
    if text == constants.ADMIN_ALERT_KEYWORD and message.reply_to_message and message.chat.type != 'private':
        # it has to be keyword and reply
        # we send details to borad group
        try:
            chat_info = bot.get_chat(message.chat.id)
            chat_identifier = chat_info.username
            if not chat_info.username:
                if str(chat_info.id).startswith('-100'):
                    chat_short_id = str(chat_info.id)[3:]
                else:
                    chat_short_id = str(chat_info.id)[1:]
                chat_identifier = f"c/{chat_short_id}"
            message_text = bot.strings.admins_chaos_disorder.format(
                chat_id=chat_identifier,
                message_id=message.reply_to_message.message_id
            )
            bot.send_message(
                settings.BOARD_GROUP_ID,
                message_text,
                parse_mode=constants.DEFAULT_PARSE_MODE
            )
            # after we send the message to board, we try to delete the message which warned us
            # but before that, let's send that user a useful tip
            try:
                bot.send_message(
                    message.from_user.id,
                    bot.strings.admins_alerted_tip_for_user,
                    parse_mode=constants.DEFAULT_PARSE_MODE
                )
            except telebot.apihelper.ApiTelegramException:
                # user blocked us
                pass
            # let's clean this mess
            bot.delete_message(message.chat.id, message.message_id)
        except telebot.apihelper.ApiTelegramException:
            # maybe we are not a member of board group?
            logging.error(traceback.format_exc())
        except:  # noqa
            # fatal error
            logging.error(traceback.format_exc())

    # check for tips
    if message.reply_to_message and message.text.startswith(constants.TIPS_HEADER):
        # search for this tip from database
        key = message.text.replace(constants.TIPS_HEADER, '', 1)
        tip = models.Tip.get(key=key)
        if tip:
            # we found a tip, let's send it
            # we send it as a reply to a message which this current message was replying to
            # but it might be deleted while we were searching for tips
            try:
                bot.reply_to(message.reply_to_message, tip.message, parse_mode=constants.DEFAULT_PARSE_MODE)
            except:  # noqa
                # we could not reply, maybe message is already deleted
                pass

    # check for admin commands
    if message.reply_to_message and text.startswith(constants.ADMIN_CMD_HEADER) and bot.is_commander(cid, uid):
        cmd = message.text.replace(constants.ADMIN_CMD_HEADER, '', 1)
        try:
            if cmd.startswith(constants.ADMIN_CMD_UNRO):
                # work on "Read-Only" stuff
                # to un-restrict the user
                restriction = models.Restriction.filter(
                    restriction_message_id=message.reply_to_message.message_id).last()
                if restriction:
                    # we try to un-restrict
                    if restriction.seconds > 0:
                        restriction.seconds -= constants.DEFUALT_RESTRICTION_SECONDS
                        try:
                            bot.restrict_chat_member(
                                message.chat.id,
                                restriction.user.uid,
                                can_send_messages=True,
                                can_send_media_messages=True,
                                can_send_other_messages=True,
                                can_add_web_page_previews=True,
                                can_invite_users=True,
                            )
                        except:  # noqa
                            logging.error(traceback.format_exc())
                        bot.reply_to(message.reply_to_message, bot.strings.restrictions_lifted,
                                     parse_mode=constants.DEFAULT_PARSE_MODE)
                    else:
                        # user has 0 (or less) restriction time, we can't do anything here
                        # we send a useful tip to user
                        bot.send_message(uid, bot.strings.restriction_cant_lift_time_too_little,
                                         parse_mode=constants.DEFAULT_PARSE_MODE)
            elif cmd.startswith(constants.ADMIN_CMD_RO):
                # to restrict user
                reason = cmd.replace(constants.ADMIN_CMD_RO, '', 1).strip()
                target_user, new = models.User.objects.get_or_create(uid=message.reply_to_message.from_user.id)
                bot.restrict_with_warning(message.reply_to_message, detected_topics=[], user=target_user, reason=reason)
            elif cmd.startswith(constants.ADMIN_CMD_CHECK):
                # we check user info and send it
                target_user, new = models.User.objects.get_or_create(uid=message.reply_to_message.from_user.id)
                if target_user:
                    try:
                        certificate = models.Certificate.filter(user=target_user).last()
                        last_restriction = models.Restriction.filter(user=target_user).last()
                        last_restriction_time = (0, 0)
                        if last_restriction:
                            delta_object = timedelta(seconds=last_restriction.seconds)
                            last_restriction_time = (delta_object.days, delta_object.seconds // 3600)
                        remaining_daily_limit = bot.get_remaining_limit(target_user)
                        detail_message = bot.strings.admin_check_user_details_template.format(
                            certificate=f"{certificate.class_name}: {certificate.percentage:.2f}%"
                            if certificate else "-",
                            last_restriction=f"{last_restriction_time[0]} kun, {last_restriction_time[1]} soat",
                            remaining_daily_limit=remaining_daily_limit
                        )
                        bot.send_message(uid, detail_message, parse_mode=constants.DEFAULT_PARSE_MODE)
                    except:  # noqa
                        logging.error(traceback.format_exc())

            elif cmd.startswith(constants.ADMIN_CMD_DELETE):
                # single message delete command without any restrictions
                bot.delete_message(message.chat.id, message.reply_to_message.id)
            bot.delete_message(cid, message.message_id)

        except:  # noqa
            bot.send_message(uid, traceback.format_exc())
            logging.error(traceback.format_exc())

    # first of all, we need to check for prohibited topics
    if should_check_for_prohibited_topics:
        detected_topics = bot.detect_prohibited_topic(text)
        if detected_topics:
            # restrict & warn
            logging.warning(f"RESTRICTING {message.chat.id=}")
            bot.restrict_with_warning(message, detected_topics, user)
            return

    # let's start code-running stuff here
    is_code, code_language = interpreter.detect_code(text)
    if is_code:
        # we have a runnable code
        # first we check if user has certificate & limit didn't exceed
        # if this is private chat, we don't set limitations & ask for certificate
        should_run = True
        if message.chat.type != 'private':
            last_certificate = models.Certificate.filter(user=user).last()
            if not last_certificate:
                should_run = False
                # user has no certificate, let's offer him/her a test
                markup = types.InlineKeyboardMarkup()
                markup.add(
                    types.InlineKeyboardButton(
                        text=bot.strings.test_start_inline_button_text,
                        callback_data=constants.CALLBACK_DATA_START_TEST_TEMPLATE.format(uid=uid)
                    )
                )
                bot.send_message(message.chat.id, bot.strings.test_should_start_for_certificate,
                                 reply_markup=markup, parse_mode=constants.DEFAULT_PARSE_MODE)
            else:
                # user has certificate. we check if s/he still can run code
                if not bot.can_run_code(message):
                    should_run = False
                    # user has already used all chances, need to wait for another day
                    bot.send_message(uid, bot.strings.code_limit_exceeded)
        if should_run:
            # run it and show response
            response_message = None
            result = None
            errors = None
            requires_input = interpreter.advanced_input_detection(text)
            if requires_input:
                # if code requires input, we do not run it
                # when user replies to it with input data, then we run and show results
                # but if bot just stays silent, it might seem weird
                # so we notify user in private about this
                try:
                    response_message = bot.send_message(
                        uid,
                        bot.strings.code_please_provide_input.format(
                            input_header=constants.DEFAULT_INPUT_HEADER),
                        parse_mode=constants.DEFAULT_PARSE_MODE
                    )
                except:  # noqa
                    # it seems that user blocked us
                    pass
            else:
                # since code doesn't require input, we run it immediately
                response = interpreter.run(code_language, text)
                errors = response.errors
                result = response.result
                if should_check_for_prohibited_topics and result:
                    # code response might include prohibited topics
                    detected_topics = bot.detect_prohibited_topic(result)
                    if detected_topics:
                        # warn & restrict
                        bot.send_message(message.chat.id, bot.strings.prohibited_topic_in_code_response)
                        bot.restrict_with_warning(message, detected_topics, user)
                        return
                formatted_output = interpreter.format_response(response)
                response_message = bot.reply_to(
                    message,
                    formatted_output,
                    parse_mode=constants.DEFAULT_PARSE_MODE
                )
                if response.errors and message.chat.type != 'private':
                    # let's send a tip to user
                    bot.send_message(
                        uid, bot.strings.code_result_errors_detected_tip,
                        parse_mode=constants.DEFAULT_PARSE_MODE
                    )
            # save the code
            code = models.Code.create(
                chat_id=message.chat.id,
                user=user,
                language_code=code_language,
                string=text,
                requires_input=requires_input,
                message_id=message.message_id,
                result=result,
                errors=errors,
                response_message_id=response_message.message_id if response_message else None
            )
            try:
                # create a reply markup to redirect user to web page to show code
                markup = types.InlineKeyboardMarkup()
                markup.add(
                    types.InlineKeyboardButton(
                        text=bot.strings.code_webview_button_text,
                        url=f"{settings.DOMAIN_URL}/code/{base64.b64encode(str(code.pk).encode()).decode()}",
                    )
                )
                bot.edit_message_reply_markup(cid, response_message.message_id, reply_markup=markup)
            except:  # noqa
                logging.error("Could not edit reply markup for message", exc_info=True)
    elif text.startswith(constants.DEFAULT_INPUT_HEADER) and message.reply_to_message:
        # if this is a reply, this might be a reply to a code
        # which means, it can be input data for that code
        # we'll check that here
        input_data = text.replace(constants.DEFAULT_INPUT_HEADER, '', 1)
        code = models.Code.get(chat_id=message.chat.id, message_id=message.reply_to_message.message_id)
        if code and code.requires_input:
            # this message was a reply to code
            response = interpreter.run(code.language_code, code.string, input_data=input_data)
            formatted_output = interpreter.format_response(response)
            bot.reply_to(
                message,
                formatted_output,
                parse_mode=constants.DEFAULT_PARSE_MODE
            )


# photo handler
@bot.message_handler(content_types=['photo'])
@lock_method_for_strangers(bot.is_member, bot.notify_about_membership)
def image_handler(message):
    uid = message.from_user.id
    user, new = models.User.objects.get_or_create(uid=uid)
    photo = message.photo[-1]
    # get the caption text
    text = message.caption if message.caption else ""
    # download the image
    dl_file = bot.download_file(bot.get_file(photo.file_id).file_path)
    img = Image.open(BytesIO(dl_file))
    # combine caption text and extracted text from image
    try:
        text = " ".join([text, pytesseract.image_to_string(img, timeout=3)])
        # check for prohibited topics
        detected_topics = bot.detect_prohibited_topic(text)
        if detected_topics:
            # restrict & warn
            bot.restrict_with_warning(message, detected_topics, user)
    except:  # noqa
        logging.error(traceback.format_exc())


# edited photo handler
@bot.edited_message_handler(content_types=['photo'])
@lock_method_for_strangers(bot.is_member, bot.notify_about_membership)
def edited_image_handler(message):
    uid = message.from_user.id
    user, new = models.User.objects.get_or_create(uid=uid)
    photo = message.photo[-1]
    # get the caption text
    text = message.caption if message.caption else ""
    # download the image
    dl_file = bot.download_file(bot.get_file(photo.file_id).file_path)
    img = Image.open(BytesIO(dl_file))
    # combine caption text and extracted text from image
    try:
        text = " ".join([text, pytesseract.image_to_string(img, timeout=3)])
        # check for prohibited topics
        detected_topics = bot.detect_prohibited_topic(text)
        if detected_topics:
            # restrict & warn
            bot.restrict_with_warning(message, detected_topics, user)
    except:  # noqa
        logging.error(traceback.format_exc())


# handler for callback queries
@bot.callback_query_handler(lambda call: True)
@lock_method_for_strangers(bot.is_member, bot.notify_about_membership)
def callback_handler(call):
    uid = call.from_user.id
    user, new = models.User.objects.get_or_create(uid=uid)
    # every single callback data has header and data
    header, data = call.data.split(constants.CALLBACK_DATA_HEADER_SEPARATOR)
    # we decide what to do according to header
    if header == constants.CALLBACK_DATA_HEADER_TEST:
        # so, test is going on
        # we check quiz and user's answer
        _, quiz_id, index, option_id, current_score = map(int, data.split(constants.CALLBACK_DATA_SEPARATOR))
        quiz = models.Quiz.get(pk=quiz_id)
        if not quiz:
            # quiz not found, maybe deleted?
            bot.send_message(
                uid,
                bot.strings.test_quiz_not_found.format(constants.COMMAND_TEST),
                parse_mode=constants.DEFAULT_PARSE_MODE
            )
        else:
            # alright, we have an existing quiz, let's start checking
            option = models.QuizOption.get(quiz=quiz, pk=option_id)
            if not option:
                # options seems to be deleted
                bot.send_message(uid, bot.strings.test_quiz_option_not_found,
                                 parse_mode=constants.DEFAULT_PARSE_MODE)
            else:
                # we have option, finally we can check
                if option.is_true:
                    # sugoi
                    current_score += 1
                # we need to build next quiz if it exists or finish the testing
                quizzes_count = models.Quiz.all().count()
                if quizzes_count == index + 1:
                    # we finished all questions, the current one was the last
                    # let's see if user has passed or failed
                    # while we check it, let's show user a message about it
                    bot.edit_message_text(
                        text=bot.strings.test_calulating_the_result,
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        parse_mode=constants.DEFAULT_PARSE_MODE
                    )
                    # and start calculations...
                    score_percentage = current_score / quizzes_count
                    if score_percentage >= constants.TEST_MIN_PASSING_SCORE_PERCENTAGE:
                        # well, user has passed the test
                        # let's define the class
                        for name, percentage, limit in constants.TEST_CLASSES_BY_RESULT:
                            if score_percentage >= percentage:
                                # we've done everything so far
                                # now only thing left is making a new certificate
                                score_percentage = int(score_percentage * 100)
                                try:
                                    image, image_name = create_certificate(
                                        *user.temp_data.split(),
                                        name,
                                        score_percentage,
                                        timezone.now().strftime("%Y-%m-%d")
                                    )
                                except:  # noqa
                                    # something really bad happened
                                    logging.error(traceback.format_exc())
                                    image = image_name = None
                                user.full_name = user.temp_data
                                user.save()
                                models.Certificate.create(
                                    user=user,
                                    score=current_score,
                                    percentage=score_percentage,
                                    class_name=name,
                                    image=File(image, name=image_name) if image else None
                                )
                                bot.send_message(
                                    uid,
                                    bot.strings.test_result_success.format(
                                        class_name=name,
                                        limit=limit
                                    ),
                                    parse_mode=constants.DEFAULT_PARSE_MODE
                                )
                                if not image:
                                    # our function could not generate image
                                    bot.send_message(
                                        uid,
                                        bot.strings.test_certificate_image_generation_failed,
                                        parse_mode=constants.DEFAULT_PARSE_MODE
                                    )
                                else:
                                    bot.send_photo(uid, image.getvalue())
                                bot.set_next_step(user, constants.STEP_INITIAL_POINT)
                                # finally, break the loop
                                break
                        else:
                            # strange, but we could not find a proper class for this score
                            bot.send_message(
                                uid,
                                bot.strings.test_class_not_found,
                                parse_mode=constants.DEFAULT_PARSE_MODE
                            )
                    else:
                        # yeah, sometimes people fail too, not only Hops
                        bot.send_message(
                            uid,
                            bot.strings.test_result_failure.format(current_score),
                            parse_mode=constants.DEFAULT_PARSE_MODE
                        )
                else:
                    # we still have another quiz(zes)
                    quiz, markup, message_string = bot.generate_quiz(call.message, index + 1, current_score)
                    if not quiz:
                        # maybe next quiz has just got deleted
                        bot.send_message(
                            uid,
                            bot.strings.test_quiz_not_found,
                            parse_mode=constants.DEFAULT_PARSE_MODE
                        )
                    else:
                        # move to next quiz
                        bot.edit_message_text(
                            text=message_string,
                            chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            reply_markup=markup,
                            parse_mode=constants.DEFAULT_PARSE_MODE
                        )
    elif header == constants.CALLBACK_DATA_HEADER_NEW_MEMBER:
        # new member is trying to read and agree on rules
        # for this to happen we need to show rules (or redirect to rules)
        user_id, chat_id = map(int, data.split(constants.CALLBACK_DATA_SEPARATOR))
        guest = models.User.get(uid=user_id)
        # the button might have been pressed by another user, in that case we just give an alert to user
        if uid != user_id:
            if guest and guest.agreement_time is not None:
                # message can be safely deleted, since user has already agreed
                bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            else:
                bot.answer_callback_query(
                    callback_query_id=call.id,
                    text=bot.strings.new_member_button_pressed_by_wrong_user,
                    show_alert=True
                )
        else:
            # right person pressed the button
            # if user has already agreed, we just finish the process here
            if guest and guest.agreement_time is not None:
                # already agreed
                bot.answer_callback_query(
                    call.id, text=bot.strings.new_member_already_agreed, show_alert=True)
                bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            else:
                # redirect him to bot chat where s/he can see rules
                cmd_data = constants.CALLBACK_DATA_HEADER_SEPARATOR.join(
                    [constants.CMD_DATA_RULES, str(call.message.chat.id)])
                bot.answer_callback_query(
                    call.id,
                    url=f"https://t.me/{bot.username}?start="
                        f"{cmd_data}"
                )
    elif header == constants.CALLBACK_DATA_HEADER_START_TEST:
        # user is gonna start a test for certification
        # we check if right user clicked
        if uid == int(data):
            # this is ok
            bot.answer_callback_query(
                call.id,
                url=f"https://t.me/{bot.username}?start={constants.CMD_DATA_START_TEST}"
            )
            bot.delete_message(call.message.chat.id, call.message.message_id)
        else:
            # someone else clicked
            bot.answer_callback_query(
                call.id,
                text=bot.strings.test_start_button_clicked_by_wrong_user,
                show_alert=True
            )
    # this is to ensure that we answered to the call
    bot.answer_callback_query(call.id)


# handler for edited messages
@bot.edited_message_handler(content_types=['text'])
@lock_method_for_strangers(bot.is_member, bot.notify_about_membership)
def edited_message_handler(message):
    uid = message.from_user.id
    cid = message.chat.id
    user, new = models.User.objects.get_or_create(uid=uid)

    # when message is edited, it migh mean:
    # - code has been edited -> we need to re-run it & edit our response
    # - just a message has been edited -> we need to check if it doesn't include prohibited topics

    should_check_for_prohibited_topics = bot.should_check_for_prohibited_topic(message)
    if should_check_for_prohibited_topics:
        detected_topics = bot.detect_prohibited_topic(message.text)
        if detected_topics:
            # warn & restrict
            bot.restrict_with_warning(message, detected_topics, user)
            return
    # it might be a code
    existing_code = models.Code.get(chat_id=cid, message_id=message.message_id)
    if existing_code:
        # it was a code before, so this might be edited version of it
        # if it is still code after editing, we edit our response,
        # otherwise we delete our response
        is_code, language = interpreter.detect_code(message.text)
        if is_code:
            requires_input = interpreter.advanced_input_detection(message.text)
            if requires_input:
                # let's send a useful tip to user
                try:
                    bot.send_message(
                        existing_code.user.uid,
                        bot.strings.code_please_provide_input.format(input_header=constants.DEFAULT_INPUT_HEADER),
                        parse_mode=constants.DEFAULT_PARSE_MODE
                    )
                except:  # noqa
                    # maybe we are blocked by user
                    pass
                # code requires input, so we can safely delete our response
                # and wait for user input
                try:
                    bot.delete_message(cid, existing_code.response_message_id)
                except:  # noqa
                    # we could not delete, maybe we never had the response :\
                    pass
            else:
                response = interpreter.run(language, message.text)
                if response.errors and message.chat.type != 'private':
                    # let's send a useful tip to user
                    try:
                        bot.send_message(
                            existing_code.user.uid, bot.strings.code_result_errors_detected_tip,
                            parse_mode=constants.DEFAULT_PARSE_MODE
                        )
                    except:  # noqa
                        # we could not send message, maybe user blocked us
                        pass
                # response may include prohibited topics
                if should_check_for_prohibited_topics and response.result:
                    detected_topics = bot.detect_prohibited_topic(response.result)
                    if detected_topics:
                        # warn & restrict
                        bot.send_message(cid, bot.strings.prohibited_topic_in_code_response)
                        bot.restrict_with_warning(message, detected_topics, user)
                        # we end process here by returning
                        return
                # checking whether it's required to edit it if we had an old response
                if existing_code.response_message_id and existing_code.result == response.result and \
                        existing_code.errors == response.errors:
                    same_result = True
                else:
                    same_result = False
                formatted_response = interpreter.format_response(response)
                existing_code.errors = response.errors
                existing_code.result = response.result
                # if we had old response, we edit it, otherwise we send new message
                if existing_code.response_message_id:
                    # we might have old response
                    try:
                        # just ignore it if the result is going to be the same
                        if not same_result:
                            bot.edit_message_text(chat_id=cid, message_id=existing_code.response_message_id,
                                                  text=formatted_response, parse_mode=constants.DEFAULT_PARSE_MODE)
                    except telebot.apihelper.ApiTelegramException:
                        # could not edit, let's try sending new message
                        resp_msg = bot.reply_to(message, formatted_response,
                                                parse_mode=constants.DEFAULT_PARSE_MODE)
                        existing_code.response_message_id = resp_msg.message_id
                else:
                    resp_msg = bot.reply_to(message, formatted_response, parse_mode=constants.DEFAULT_PARSE_MODE)
                    existing_code.response_message_id = resp_msg.message_id
            # save all changes
            existing_code.string = message.text
            existing_code.language_code = language
            existing_code.requires_input = requires_input
            existing_code.save()

# --- END: definition of bot instance
