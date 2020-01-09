from rest_framework import serializers

from . import models


class TweetOptionSerializer(serializers.ModelSerializer):
    
    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(TweetOptionSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = models.TweetOption
        fields = [
            'pk',
            'user_id',
            'option',
            'tweet_id',
        ]