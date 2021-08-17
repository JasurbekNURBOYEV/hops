from django.contrib import admin

from core import models


class QuizOptionInline(admin.StackedInline):
    exclude = ['created_time', 'last_updated_time']
    model = models.QuizOption
    extra = 4


@admin.register(models.Quiz)
class QuizAdmin(admin.ModelAdmin):
    inlines = [QuizOptionInline]


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ["uid", "full_name"]


admin.site.register(models.Certificate)
admin.site.register(models.Tip)
