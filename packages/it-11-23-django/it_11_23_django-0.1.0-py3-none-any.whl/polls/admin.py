from django.contrib import admin

from . import models


class ChoiceInline(admin.StackedInline):
    model = models.Choice


class QuestionAdmin(admin.ModelAdmin):
    list_display = ["question_text", "pub_date", "was_published_recently"]
    fieldsets = [
        ("Basic", {"fields": ["question_text"]}),
        ("Date information", {"fields": ["pub_date"]}),
    ]
    inlines = [ChoiceInline]
    sortable_by = ["question_text", "pub_date"]
    list_filter = ["pub_date"]
    search_fields = ["question_text"]


admin.site.register(models.Question, QuestionAdmin)
admin.site.register(models.Choice)
