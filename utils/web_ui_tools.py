import json

from telebot.types import Dictionaryable, JsonSerializable


class WebButton(Dictionaryable, JsonSerializable):
    def __init__(self, text, url):
        self.text = text
        self.url = url

    def to_json(self):
        return json.dumps(self.do_dict())

    def to_dict(self):
        return {"text": self.text, "web_app": {"url": self.url}}
