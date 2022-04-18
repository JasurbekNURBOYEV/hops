from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import ModelSerializer, SerializerMethodField, CharField, \
    IntegerField, Serializer, PrimaryKeyRelatedField

from core.models import User
from greed_island.models import Tag


class TagSerializer(ModelSerializer):
    author = CharField(read_only=True, source="author.full_name")
    subscribers_count = IntegerField(read_only=True)
    asked_count = SerializerMethodField(read_only=True)
    is_subscribed = SerializerMethodField(read_only=True)

    def get_asked_count(self, instance):  # noqa
        return instance.questions.count()

    def get_is_subscribed(self, instance):  # noqa
        return instance.pk in self.context["subscribed_tags"]

    class Meta:
        model = Tag
        fields = ("id", "name", "author", "subscribers_count", "asked_count", "is_subscribed")


class TagRequestSerializer(Serializer):
    user = SlugRelatedField(slug_field='uuid', queryset=User.all())
    tags = PrimaryKeyRelatedField(queryset=Tag.all(), many=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        tag = Tag.all().first()

        user = validated_data["user"]
        tags = validated_data["tags"]
        for tag in Tag.all():
            if tag not in tags:
                tag.subscribers.remove(user)
            else:
                tag.subscribers.add(user)

        return tag
