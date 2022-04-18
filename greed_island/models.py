from django.db import models

from core.models import BaseLayer, User


class MessageMixin(models.Model):
    """
    We are going to use this mixin for all models related to Telegram message.
    """
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    chat_id = models.BigIntegerField(default=0)
    message_id = models.PositiveBigIntegerField(null=True)
    reply_to_message_id = models.PositiveBigIntegerField(null=True)

    def __str__(self):
        return f"{self.text}"

    class Meta:
        abstract = True


class Tag(BaseLayer):
    """
    Tag is what specifies category of a question. A question may include multiple tags.
    Do you remember the "game of tags"? If tag is your target, then you should get it at any cost.
    We'll make it possible by any means.
    We still lack certain things: card, its specs, implementation. I don't even know how to imagine it. Need more time.
    """
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=127, unique=True)
    subscribers = models.ManyToManyField(User, related_name='tags', blank=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        db_table = 'tags'


class Question(BaseLayer, MessageMixin):
    """
    This is a question, like a task to achieve a card.
    You answer the question, owner approves, you get the card.
    However, I'm not sure about the card part yet. It is super complicated even to think about it.
    Implementation details fall far beyond that complexity level...
    """
    tags = models.ManyToManyField(Tag, related_name='questions')

    class Meta:
        db_table = 'questions'


class Answer(BaseLayer, MessageMixin):
    """
    Answer to Question. May be true, may be false. It is up to owner to decide.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    is_accepted = models.BooleanField(default=False)

    class Meta:
        db_table = 'answers'


class Comment(BaseLayer, MessageMixin):
    """
    Basically to save every single message that is a reply to another message
    """
    class Meta:
        db_table = 'comments'
