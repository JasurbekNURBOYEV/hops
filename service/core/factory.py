"""
This is a bot factory module which is roughly used to create full bot instance
"""
# --- START: IMPORTS
# built-in
from typing import List
from random import shuffle
import logging
import traceback

# local
from service.core import models
from service.utils.decorators import lock_method_for_strangers
from service.core import constants
from service.core.strings import Strings
from service.core.certificate import create_certificate
from service.utils.rex import Interpreter

# django-specific
from django.core.files import File
from django.utils import timezone
from django.conf import settings

# other/external
import telebot
from telebot import types

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
        try:
            member = self.get_chat_member(settings.MAIN_GROUP_ID, uid)
        except telebot.apihelper.ApiTelegramException:
            try:
                member = self.get_chat_member(settings.TEST_GROUP_ID, uid)
            except telebot.apihelper.ApiTelegramException:
                pass
        finally:
            # we might get member, but status might be 'left'
            if member and member.status != constants.USER_STATUS_LEFT:
                return True
            elif uid in whitelist:
                # whitelist is a whitelist, we don't lock whitelisted users
                return True
            return False

    def notify_about_membership(self, message) -> None:
        self.send_message(message.from_user.id, "You have to be a member of main group")

    def welcome(self, message) -> None:
        """
        Send a welcome message and store user (if new)
        :param message: message object by telebot
        :return: None
        """
        uid = message.from_user.id
        instance, new = models.User.objects.get_or_create(uid=uid)
        if new:
            # we have a new user
            self.send_message(chat_id=uid, text="Hola")
        else:
            self.send_message(uid, "Hey!")
        # TODO: complete this, because it is incomplete

    def set_next_step(self, user: models.User, step: int, temp_data: str = None) -> None:
        """
        Just to save current step of user
        :param user: user instance
        :param step: int representing the current step
        :param temp_data: temporary data refers to string data which can be used to store some little data for steps
        :return: none
        """
        user.step = step
        user.temp_data = temp_data
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


# --- START: definition of bot instance
# initialize a bot instance
bot = HopsBot(token=settings.BOT_TOKEN)


# command handlers
@bot.message_handler(commands=[constants.COMMAND_START, constants.COMMAND_CANCEL, constants.COMMAND_TEST])
@lock_method_for_strangers(checker=bot.is_member, default=bot.notify_about_membership)
def command_handler(message):
    text = message.text
    command = text[1:]
    uid = message.from_user.id
    user, _ = models.User.objects.get_or_create(uid=uid)

    # start command
    if command.startswith(constants.COMMAND_START) and message.chat.type == 'private':
        # check if it is a data-binded command
        data = command.replace(constants.COMMAND_START, '', 1)
        if not data:
            # it is a pure command without additional data
            # we need to do tha basic start procedure
            bot.welcome(message)
        else:
            # we have data which needs processing
            if data == constants.CMD_DATA_START_TEST:
                # register the step & start
                bot.set_next_step(user, constants.STEP_TEST_WAITING_TO_START)
                bot.send_message(uid, text=bot.strings.start_test)
                # hopefully we're done here
    elif command.startswith(constants.COMMAND_CANCEL) and message.chat.type == 'private':
        # this is where we handle cancellations
        # in any case, we just cancel whatever we were doing
        # and just head back to initial state
        bot.set_next_step(user=user, step=constants.STEP_INITIAL_POINT)
        bot.send_message(uid, bot.strings.cancelled)
    elif command.startswith(constants.COMMAND_TEST) and message.chat.type == 'private':
        # register the step & start
        bot.set_next_step(user, constants.STEP_TEST_WAITING_TO_START)
        bot.send_message(uid, text=bot.strings.start_test)


# here we try to handle text messages
@bot.message_handler(content_types=['text'])
@lock_method_for_strangers(checker=bot.is_member, default=bot.notify_about_membership)
def text_handler(message):
    uid = message.from_user.id
    text = message.text
    user, new = models.User.objects.get_or_create(uid=uid)
    # what we do here is basically working with steps
    # we do whatever necessary according the current state of the user
    # so, let's start by checking steps
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
                # what kinda name would include numbers? well, it would if you were the son of Elon,
                # well, i'm 100% sure, that boy will never use the bot, so it is safe to do this.
                bot.send_message(uid, bot.strings.test_full_name_invalid)
    # this is our main group chat (or other group chat)
    # what can we do in group:
    # + detect prohibited topics
    # + run code
    # + handle management commands
    # + what else?..

    # first of all, we need to check for prohibited topics
    # TODO: implement detection for prohibited topics

    # let's start code-running stuff here
    is_code, code_language = interpreter.detect_code(text)
    if is_code:
        # we have a runnable code
        # run it and show response
        requires_input = interpreter.advanced_input_detection(text)
        if requires_input:
            # if code requires input, we do not run it
            # when user replied to it with input data, then we run and show results
            # but if bot just stays silent, it might seem weird
            # so we notify user in private about this
            bot.send_message(uid, bot.strings.code_please_provide_input)
        else:
            # since code doesn't require input, we run it immediately
            response = interpreter.run(code_language, text)
            formatted_output = interpreter.format_response(response)
            bot.reply_to(
                message,
                formatted_output,
                parse_mode=constants.DEFAULT_PARSE_MODE
            )
            if response.errors and message.chat.type != 'private':
                # let's send a tip to user
                bot.send_message(
                    uid, bot.strings.code_result_errors_detected_tip, parse_mode=constants.DEFAULT_PARSE_MODE
                )
        models.Code.create(
            chat_id=message.chat.id,
            user=user,
            language_code=code_language,
            string=text,
            requires_input=requires_input,
            message_id=message.message_id
        )
    elif text.startswith(constants.DEFAULT_INPUT_HEADER) and message.reply_to_message:
        # if this is a reply, this might be reply to a code
        # which means, it can be input data for that code
        # we'll check that here
        input_data = text.replace(constants.DEFAULT_INPUT_HEADER, 1)
        code = models.Code.get(message_id=message.reply_to_message.message_id)
        if code and code.requires_input:
            # this message was a reply to
            response = interpreter.run(code.language_code, code.string, input_data=input_data)
            formatted_output = interpreter.format_response(response)
            bot.reply_to(
                message,
                formatted_output,
                parse_mode=constants.DEFAULT_PARSE_MODE
            )


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
                bot.send_message(uid, bot.strings.test_quiz_option_not_found, parse_mode=constants.DEFAULT_PARSE_MODE)
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
                                except Exception as e:
                                    # something really bad happened
                                    logging.error(traceback.format_exc())
                                    image = image_name = None
                                user.full_name = user.temp_data
                                user.save()
                                certificate = models.Certificate.create(
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

    # this is to ensure that we answered to the call
    bot.answer_callback_query(call.id)

# --- END: definition of bot instance
