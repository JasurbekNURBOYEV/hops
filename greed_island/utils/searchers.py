"""
Looking for something? Probably yes.
"""
import logging
from typing import List, Tuple

from telebot.types import Message

from core.strings import Strings

strings = Strings()


class Search(object):

    @staticmethod
    def extract_tag(text: str, offset: int, length: int) -> str:
        """
        Extract tag from message text
        :param text: input text message
        :param offset: offset
        :param length: length
        :return: tag
        """
        return text[offset + 1:offset + length]

    @staticmethod
    def collect_question_tags(message: Message) -> Tuple[List[str], int, int]:
        """
        We try to find tags from message object from Telegram
        :param message: Telegram message object
        :return: list of tags as string, start of tag index, index of end of tag line
        """
        # i thought a lot about tag detection mechanism.
        # whatever i choose - there is always downsides, issues.
        # final result: i will extract only tags within the same line with question tag.
        # for that, i should detect line of the question tag first.
        # then i only take tags between question tag and end of line.

        # the variable below indicates index end of the line where question tag is located
        start_of_world = 0
        end_of_world = 0

        entities = message.entities or message.caption_entities
        hashtags = [tag for tag in entities if tag.type == 'hashtag']
        tags = []
        text = message.text or message.caption

        # identify the index of 'end of line' char for tags
        # we stop looking for tags after that index
        for tag in hashtags:
            tag_data = Search.extract_tag(text, tag.offset, tag.length)
            if tag_data == strings.gi_question_tag:
                # let's start the walk
                start_of_world = tag.offset
                end_of_world = tag.offset + tag.length
                for char in text[tag.offset + tag.length:]:
                    end_of_world += 1
                    if char == '\n':
                        # we reached the end of line
                        break
                else:
                    # we couldn't reach end of line
                    # probably the question text ended at the same line with question tag
                    # restore the indicator to end of tag
                    end_of_world = tag.offset + tag.length

        for tag in hashtags:
            # collect tags within allowed area
            if start_of_world < tag.offset < end_of_world:
                tag_data = Search.extract_tag(text, tag.offset, tag.length)
                if tag_data not in (strings.gi_question_tag, strings.gi_answer_tag):
                    tags.append(tag_data)

        return tags, start_of_world, end_of_world

    @staticmethod
    def is_question(message: Message) -> bool:
        """
        Used to identify if the message is a question or not.
        If message contains a question tag, then it is a question.
        :param message: Telegram message object
        :return: True - question, False  - not question
        """
        text = message.text or message.caption
        entities = message.entities or message.caption_entities
        if entities:
            for entity in entities:
                # entity has to be tag, otherwise, what's the point on checking it?
                if entity.type == 'hashtag':
                    tag_data = Search.extract_tag(text, entity.offset, entity.length)
                    logging.info(f'Tag data: {tag_data}')
                    if tag_data == strings.gi_question_tag:
                        return True
        return False

    @staticmethod
    def is_answer(message: Message) -> Tuple[bool, int, int]:
        """
        Used to identify if the message is an answer or not.
        If message contains a answer tag, then it is an answer.
        :param message: Telegram message object
        :return: tuple(is_answer, offset of tag, lentght of tag)
        """
        # all answers are replied to an exact question
        entities = message.entities or message.caption_entities
        if message.reply_to_message and entities:
            for entity in entities:
                tag_data = Search.extract_tag(message.text or message.caption, entity.offset, entity.length)
                if entity.type == 'hashtag' and tag_data == strings.gi_answer_tag:
                    return True, entity.offset, entity.length
            else:
                return False, 0, 0

    @staticmethod
    def clean_answer(message: Message) -> str:
        """
        Used to clean answer. For now we just remove tag from answer
        :param message: Message instance
        :return: clean text
        """
        start = length = 0
        text = message.text or message.caption
        entities = message.entities or message.caption_entities
        for entity in entities:
            tag_data = Search.extract_tag(text, entity.offset, entity.length)
            if entity.type == 'hashtag' and tag_data == strings.gi_answer_tag:
                start, length = entity.offset, entity.length
        if text:
            return f'{text[:start]}{text[start + length:]}'.strip()
        return text
