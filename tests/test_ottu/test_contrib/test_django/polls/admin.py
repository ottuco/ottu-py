from django.contrib import admin

from .models import Poll


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ("question",)
