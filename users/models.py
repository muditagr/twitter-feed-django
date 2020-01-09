from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(_("Name of User"), blank=True, null=True, max_length=255)

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})



class TweetOption(models.Model):
    """Model definition for TweetOption."""
    OPTION_1 = 1
    OPTION_2 = 2
    OPTION_3 = 3
    option_choices = (
        (OPTION_1, 'option_1'),
        (OPTION_2, 'option_2'),
        (OPTION_3, 'option_3')
    )
    user_id = models.CharField(max_length=32)
    tweet_id = models.CharField(max_length=20)
    option = models.CharField(max_length=4, choices=option_choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:

        verbose_name = 'TweetOption'
        verbose_name_plural = 'TweetOptions'
        unique_together = ('user_id', 'tweet_id')


class TwitterAccessToken(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='twitter_access_token', on_delete=models.CASCADE)
    access_token = models.CharField(max_length=254)
    token_secret = models.CharField(max_length=254)
    twitter_user_id = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
