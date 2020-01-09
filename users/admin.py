from django import forms
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

from . import models

class TweetOptionAdminForm(forms.ModelForm):

    class Meta:
        model = models.TweetOption
        fields = "__all__"


class TweetOptionAdmin(admin.ModelAdmin):
    form = TweetOptionAdminForm
    list_display = [
        "user_id",
        "tweet_id",
        "option",
    ]
    readonly_fields = [
        "user_id",
        "tweet_id",
        "option",
    ]


admin.site.register(models.TweetOption, TweetOptionAdmin)
