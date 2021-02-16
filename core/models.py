# --- START: IMPORTS

# built-in
# local
from django.conf import settings

from core import constants

# django-specific
from django.db import models
from django.utils import timezone

# other/external
# --- END: IMPORTS


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
    default_manager = BaseManager
    objects = BaseManager
    all_objects = models.Manager

    # all models are going to have following two fields
    created_time = models.DateTimeField(default=timezone.now)
    last_updated_time = models.DateTimeField(default=timezone.now)

    @classmethod
    def create(cls, *args, **kwargs):
        now = timezone.now()
        obj = cls(
            *args,
            **kwargs,
            created_time=now,
            last_updated_time=now
        )
        obj.save()
        return obj

    def save(self, *args, **kwargs):
        self.last_updated_time = timezone.now()
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
    full_name = models.TextField(null=True)
    step = models.PositiveSmallIntegerField(default=0)
    temp_data = models.TextField(null=True)
    magic_word = models.CharField(max_length=63)
    welcome_message_id = models.IntegerField(null=True)
    agreement_time = models.DateTimeField(null=True)

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


class Certificate(BaseLayer):
    """
    Certificate model stores the certification time, scores, class and all other details
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='certificates')
    score = models.PositiveSmallIntegerField()
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    class_name = models.CharField(max_length=7)
    image = models.ImageField(upload_to='certificates', null=True)

    @classmethod
    def create(cls, user, score, percentage, class_name, image=None):
        # we set limit to store certificates
        # one user can get unlimited certificates, but we store only the last 3 of them
        # because we don't want to fill our storage with redundant garbage
        instances = cls.objects.filter(user=user)
        if instances.count() >= constants.DEFAULT_CERT_LIMIT:
            instances.order_by('-created_time').last().delete()
        return super().create(
            user=user, score=score, percentage=percentage, class_name=class_name, image=image
        )

    def delete(self, using=None, keep_parents=False):
        # when we delte certificate, its image should also be deleted
        if self.image.storage.exists(self.image.name):
            self.image.storage.delete(self.image.name)
        super(Certificate, self).delete(using=using, keep_parents=keep_parents)

    def __str__(self):
        if self.user.full_name:
            return ''.join([self.user.full_name[:30], ['', '...'][len(self.user.full_name) > 30]])
        return f"{self.class_name}: {self.percentage}"

    class Meta:
        db_table = 'certificates'


class Code(BaseLayer):
    """
    To store runnable codes and their details
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='codes')
    string = models.CharField(max_length=4095)
    language_code = models.PositiveSmallIntegerField()
    requires_input = models.BooleanField(default=False)
    errors = models.TextField(null=True)
    result = models.TextField(null=True)
    chat_id = models.IntegerField()
    message_id = models.IntegerField()
    response_message_id = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.user}: {self.language_code}"

    class Meta:
        db_table = 'codes'


class Restriction(BaseLayer):
    """
    To log restriction history
    """
    user = models.ForeignKey(User, models.CASCADE, related_name='restrictions')
    seconds = models.IntegerField()
    restriction_message_id = models.IntegerField(null=True)

    class Meta:
        db_table = 'restrictions'


class Tip(BaseLayer):
    """
    We will store useful tips here
    """
    key = models.CharField(max_length=15, unique=True)
    message = models.TextField()

    def __str__(self):
        return f"{self.key}: {''.join([self.message[:30], ['', '...'][len(self.message) > 30]])}"

    class Meta:
        db_table = 'tips'
