from django.db import models
from datetime import datetime


class BaseLayer(models.Model):
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
