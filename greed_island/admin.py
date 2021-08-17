from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from greed_island.factory import bot
from greed_island.models import Tag, Question, Answer
from greed_island.utils.uris import URIfy

urify = URIfy(bot)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'subscribed', 'asked')
    autocomplete_fields = ['author']
    readonly_fields = ('author', 'subscribers', 'created_time', 'last_updated_time')
    search_fields = ('name',)
    sortable_by = ('name',)

    def get_queryset(self, request):
        # to order results by frequence: trending tags first
        queryset = super(TagAdmin, self).get_queryset(request)
        return queryset.annotate(asked_count=Count('questions')).order_by('-asked_count')

    def subscribed(self, obj):
        return obj.subscribers.all().count()

    def asked(self, obj):
        return obj.questions.all().count()


class AnswerInline(admin.StackedInline):
    exclude = ['created_time', 'last_updated_time']
    model = Answer
    fields = ('author', 'is_accepted', 'text')
    readonly_fields = fields
    list_display = fields
    extra = 0

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    fields = ('text', 'author', 'tag', 'created_time', 'chat_id', 'discussion', 'message')
    list_display = ('text', 'author', 'tag')
    readonly_fields = fields
    search_fields = ('text', 'tags__name')
    inlines = [AnswerInline]

    def tag(self, obj):
        return ', '.join([i.name for i in obj.tags.all()])

    def discussion(self, obj):
        return format_html(
            f'<a href="{urify.get_message_thread_link(obj.chat_id, obj.message_id)}">Muhokamaga o\'tish</a>'
        )

    def message(self, obj):
        return format_html(
            f'<a href="{urify.get_message_link(obj.chat_id, obj.message_id)}">Xabarga o\'tish</a>'
        )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
