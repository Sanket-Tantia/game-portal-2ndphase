from rest_framework import serializers
from deskapp.models import GameRound, TokenPlayLog


class GameRoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameRound
        fields = ('username', 'session', 'tokens_playing_for', 'tokens_won', 'tokens_remaining', 'won_on_number', 'is_jackpot')


class TokenPlayLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TokenPlayLog
        fields = ('retailer', 'token_amount')
