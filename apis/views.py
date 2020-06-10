from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db import connection

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from deskapp.models import GameRound, Profile, AvailableToken, TokenPlayLog, GrantedToken
from .serializers import GameRoundSerializer, TokenPlayLogSerializer

from django.contrib.auth.models import User
from django.contrib.auth import authenticate


# Create your views here.
class GameRoundListView(APIView):
    def get(self, request, session):
        all_rounds = GameRound.objects.filter(session=session)
        serializer = GameRoundSerializer(all_rounds, many=True)
        responseBody = {'ResponseStatus': '200_OK',
                        'ResponseMessage': serializer.data}
        return Response(responseBody, status=status.HTTP_200_OK)


class GameRoundCreateView(APIView):
    def post(self, request):
        granted_token_obj = GrantedToken.objects.get(pk=request.data.get('session'))
        granted_token_obj.token_amount = int(request.data.get('tokens_remaining'))
        granted_token_obj.save()

        serializer = GameRoundSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            responseBody = {'ResponseStatus': '201_CREATED'}
            return Response(responseBody, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserGameProfileView(APIView):
    def post(self, request):
        session = request.data.get('session')
        username = request.data.get('username')

        try:
            token_amount = GrantedToken.objects.get(pk=session).token_amount
        except GrantedToken.DoesNotExist:
            token_amount = 0

        probability = Profile.objects.get(username=username).probability
        # print(queryset.query)

        body = {
            'username': username,
            'session': session,
            'token_granted': token_amount,
            'probability': probability
        }

        responseBody = {'ResponseStatus': '200_OK', 'ResponseMessage': body}
        return Response(responseBody, status=status.HTTP_200_OK)


class UserRefillTokenView(APIView):
    def post(self, request):
        playLogData = {
            'retailer': request.data.get('username'),
            'token_amount': request.data.get('token_amount'),
        }

        granted_token_obj = GrantedToken.objects.get(pk=request.data.get('session'))
        granted_token_obj.token_amount = granted_token_obj.token_amount + int(request.data.get('token_amount'))
        granted_token_obj.save()

        serializer = TokenPlayLogSerializer(data=playLogData)
        if serializer.is_valid():
            serializer.save()
            responseBody = {'ResponseStatus': '200_OK'}
            return Response(responseBody, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAuthorizeRefillView(APIView):
    def post(self, request):
        try:
            username = User.objects.get(id=request.data.get('username')).username
        except Exception as e:
            responseBody = {'ResponseStatus': '401_UNAUTHORIZED', 'ResponseMessage': "User does not exist"}
            return Response(responseBody, status=status.HTTP_401_UNAUTHORIZED)
        user = authenticate(request, username=username, password=request.data.get('password'))
        if user is not None:
            token_amount = AvailableToken.objects.get(username=user.id).token_amount
            
            body = {
                'username': user.id,
                'available_token': token_amount
            }

            responseBody = {'ResponseStatus': '200_OK', 'ResponseMessage': body}
            return Response(responseBody, status=status.HTTP_200_OK)
        else:
            responseBody = {'ResponseStatus': '401_UNAUTHORIZED', 'ResponseMessage': "Username or password is incorrect"}
            return Response(responseBody, status=status.HTTP_401_UNAUTHORIZED)
