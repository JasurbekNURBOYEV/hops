from django.db import models
from datetime import datetime


class BaseManager(models.Manager):
    """
    Our basic manager is used to order all child models of BaseLayer
    to be ordered by created time (descending), therefore it creates a LIFO order,
    causing the recent ones appear first in results.
    """
    use_for_related_fields = True

    def get_queryset(self):
        super(BaseManager, self).get_queryset().order_by('-created_time')


class BaseLayer(models.Model):
    """
    This layer makes system-wide sonfigurations which tends to be effective for every single model.
    It is used as a parent class for all other models.
    """

    # let's configure managers
    default_manager = BaseManager()
    objects = BaseManager()
    all_objects = models.Manager()

    # all models are going to have following two fields
    created_time = models.DateTimeField()
    last_updated_time = models.DateTimeField()

    @classmethod
    def create(cls, *args, **kwargs):
        now = datetime.now()
        obj = cls(
            *args,
            **kwargs,
            created_time=now,
            last_updated_time=now
        )
        obj.save()
        return obj

    def save(self, *args, **kwargs):
        self.last_updated_time = datetime.now()
        return super(BaseLayer, self).save(*args, **kwargs)

    @classmethod
    def get(cls, *args, **kwargs):
        try:
            return cls.objects.get(*args, **kwargs)
        except cls.DoesNotExist:
            return None

    @classmethod
    def all(cls, *args, **kwargs):
        return cls.objects.all()

    @classmethod
    def filter(cls, *args, **kwargs):
        return cls.objects.filter(*args, **kwargs)

    class Meta:
        abstract = True


class User(BaseLayer):
    """
    To store users
    """
    uid = models.IntegerField(unique=True)

    def __str__(self):
        return f"User: {self.uid}"

    class Meta:
        db_table = 'users'


class Quiz(BaseLayer):
    """
    A simple quiz model to store quizzes
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='quizzes')
    question = models.TextField()

    def __str__(self):
        return f"{''.join([self.question[:30], ['', '...'][len(self.question) > 30]])}"

    class Meta:
        db_table = 'quizzes'


class QuizOption(BaseLayer):
    """
    A single quiz can have multiple options/answers.
    So, we are using ManyToOne relation
    """
    quiz = models.ForeignKey(Quiz, on_delete=models.SET_NULL, null=True, related_name='options')
    text = models.TextField()
    is_true = models.BooleanField(default=False)

    def __str__(self):
        return f"{''.join([self.text[:30], ['', '...'][len(self.text) > 30]])}"

    class Meta:
        db_table = 'options'
