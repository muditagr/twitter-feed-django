from django.urls import include, path
from home.api.v1 import viewsets
from home.api.v1.viewsets import (UserTimeLineView,
                                  twitter_get_oauth_request_token,
                                  twitter_get_oauth_token, TweetOptionViewSet)
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('tweetoptions',TweetOptionViewSet, base_name='tweetoptions')
router.register('user-timeline', UserTimeLineView, base_name='user-time-line')
router.register('like-tweet',viewsets.LikeTweetView, base_name='like-tweet')
router.register('retweet',viewsets.ReTweetView, base_name='retweet')

urlpatterns = [
    path("", include(router.urls)),
    path('request-token/', twitter_get_oauth_request_token.as_view(), name="get-request-token"),
    path('access-token/', twitter_get_oauth_token.as_view(), name='get-access-token')
]
