import base64
import json
from urllib.parse import parse_qsl

import requests
from django import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.http import urlencode
from home.api.v1.serializers import UserSerializer
from requests_oauthlib import OAuth1
from rest_framework import status
from rest_framework.authentication import (SessionAuthentication,
                                           TokenAuthentication)
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ViewSet
from users.models import TwitterAccessToken
from users.serializers import TweetOptionSerializer


consumer_key = 'GzmrVaxsbMLQlfd1SV4Rp4ym9'
consumer_secret = '7VEDnD1nOPFmBKza0LVg4GPyYfLdUESg8HFXCdmAZ362Hlqbnt'



def get_oauth_obj(access_token, token_secret):
    oauth = OAuth1(
            client_key=consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=token_secret
        )
    return oauth

class OAuthError(Exception):
    pass

class twitter_get_oauth_request_token(APIView):
    def get(self, request, format=None):
        oauth = OAuth1(
            client_key=consumer_key,
            client_secret=consumer_secret
        )
        rt_url = 'https://api.twitter.com/oauth/request_token'
        response = requests.post(url=rt_url, auth=oauth)
        if response.status_code in [200, 201]:
            self.request_token = dict(parse_qsl(response.text))
            request.session['oauth_request_token'] = self.request_token
            return Response({
                'request_oauth_token': self.request_token['oauth_token'],
                # 'url': 'https://api.twitter.com/oauth/authenticate?oauth_token={}&oauth_callback=http://127.0.0.1:8000/api/v1/access-token/'.format(self.request_token['oauth_token'])
            })
        else:
            pass


class twitter_get_oauth_token(APIView):
    def get(self, request, format=None):
        # request_token = _get_rt_from_session(request)
        request_token = request.GET.get('oauth_token')
        oauth = OAuth1(
            client_key=consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=request_token,
        )
        oauth_verifier = request.GET.get('oauth_verifier')
        at_url = 'https://api.twitter.com/oauth/access_token'

        if oauth_verifier:
                at_url = at_url + '?' + urlencode(
                    {'oauth_verifier': oauth_verifier})
        response = requests.post(at_url, auth=oauth)
        if response.status_code not in [200, 201]:
            raise OAuthError("Error getting a Access token: {}".format(response.text))
        access_token = dict(parse_qsl(response.text))
        request.session['oauth_access_token'] = access_token

        t_user_info = twitter_user_info(request)

        email = t_user_info['email']
        User = get_user_model()

        if not email:
            return Response({'message': 'Please Add and verify email to twitter account'}, status=status.HTTP_401_UNAUTHORIZED)

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'name': t_user_info['name'],
                'username': t_user_info['screen_name']
            }
        )
        token, created = Token.objects.get_or_create(user=user)
        t_at, created = TwitterAccessToken.objects.get_or_create(
            user=user,
            defaults={
                'access_token':access_token['oauth_token'],
                'token_secret':access_token['oauth_token_secret'],
                'twitter_user_id':t_user_info['id']
            }
        )
        user_serializer = UserSerializer(user)
        return Response({
            'token': token.key,
            'user': user_serializer.data,
            'twitter_user_id': t_user_info['id']
            })


def _get_rt_from_session(request):
    """
    Returns the request token cached in the session
    """
    try:
        return request.session['oauth_request_token']
    except KeyError:
        raise OAuthError('No request token saved')

def twitter_user_info(request):
    access_token = request.session['oauth_access_token']
    oauth = OAuth1(
        client_key=consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token['oauth_token'],
        resource_owner_secret=access_token['oauth_token_secret']
    )

    verify_url = 'https://api.twitter.com/1.1/account/verify_credentials.json'
    params = {"include_email": 'true'}

    verify_url = verify_url + '?' + urlencode(params)
    verify_res = requests.get(verify_url, auth=oauth)

    if verify_res.status_code == 200:
        return verify_res.json()
    else:
        raise OAuthError("Invalid user")


class UserTimeLineView(ViewSet):
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    def list(self, request, format=None):
        user = request.user
        access_token = TwitterAccessToken.objects.filter(user=user).first()

        if not user or not access_token:
            return Response({'message': "User or Token not found"}, status=status.HTTP_401_UNAUTHORIZED)

        # oauth = OAuth1(
        #     client_key=consumer_key,
        #     client_secret=consumer_secret,
        #     resource_owner_key=access_token.access_token,
        #     resource_owner_secret=access_token.token_secret
        # )

        oauth = get_oauth_obj(access_token.access_token, access_token.token_secret)
        url = "https://api.twitter.com/1.1/statuses/home_timeline.json"

        params = {
            'count': 100,
            }

        response = requests.get(
            url,
            params=params,
            auth=oauth
        )

        if response.status_code == 200:
            return Response(response.json(), status=status.HTTP_200_OK)
        else:
            return Response(response.json())

class LikeTweetView(ViewSet):
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    def create(self, request, format=None):
        user = request.user
        access_token = TwitterAccessToken.objects.filter(user=user).first()

        tweet_id = request.data.get('tweet_id')

        if not user or not access_token:
            return Response({'message': "User or Token not found"}, status=status.HTTP_401_UNAUTHORIZED)

        # oauth = OAuth1(
        #     client_key=consumer_key,
        #     client_secret=consumer_secret,
        #     resource_owner_key=access_token.access_token,
        #     resource_owner_secret=access_token.token_secret
        # )
        oauth = get_oauth_obj(access_token.access_token, access_token.token_secret)
        url = "https://api.twitter.com/1.1/favorites/create.json"

        params = {
            'id': tweet_id
            }

        response = requests.post(
            url,
            params=params,
            auth=oauth
        )

        return Response(response.json(), status=response.status_code)


class ReTweetView(ViewSet):
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    def create(self, request, format=None):
        user = request.user
        access_token = TwitterAccessToken.objects.filter(user=user).first()

        tweet_id = request.data.get('tweet_id')

        if not user or not access_token:
            return Response({'message': "User or Token not found"}, status=status.HTTP_401_UNAUTHORIZED)

        # oauth = OAuth1(
        #     client_key=consumer_key,
        #     client_secret=consumer_secret,
        #     resource_owner_key=access_token.access_token,
        #     resource_owner_secret=access_token.token_secret
        # )
        oauth = get_oauth_obj(access_token.access_token, access_token.token_secret)
        url = "https://api.twitter.com/1.1/statuses/retweet/:id.json"

        params = {
            'id': tweet_id
            }

        response = requests.post(
            url,
            params=params,
            auth=oauth
        )
        if response.status_code == 200:
            oauth = get_oauth_obj(access_token.access_token, access_token.token_secret)
            url = "https://api.twitter.com/1.1/statuses/retweet/:id.json"

            params = {
                'id': tweet_id
                }

            response = requests.post(
                url,
                params=params,
                auth=oauth
            )

        return Response(response.json(), status=response.status_code)


class TweetOptionViewSet(ModelViewSet):
    """ViewSet for the TweetOption class"""

    serializer_class = TweetOptionSerializer
    # permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = TweetOption.objects.all()
        user_id = self.request.query_params.get('user_id', None)
        tweet_id = self.request.query_params.get('tweet_id', None)
        if user_id and tweet_id:
            queryset  = queryset.filter(user_id=user_id, tweet_id=tweet_id)
        return queryset

