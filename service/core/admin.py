from django.contrib import admin
from service.core import models


class QuizOptionInline(admin.StackedInline):
    exclude = ['created_time', 'last_updated_time']
    model = models.QuizOption
    extra = 4


@admin.register(models.Quiz)
class QuizAdmin(admin.ModelAdmin):
    inlines = [QuizOptionInline]


admin.site.register(models.User)
# admin.site.register(QuizAdmin)
admin.site.register(models.Certificate)
