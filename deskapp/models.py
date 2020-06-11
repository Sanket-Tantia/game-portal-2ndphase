from django.db import models
from django.contrib.auth.models import User

from datetime import datetime

# Create your models here.
class Profile(models.Model):
    username = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    fullname = models.CharField(max_length=255)
    phone = models.CharField(max_length=10)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    winx = models.IntegerField(blank=True, null=True)
    probability = models.IntegerField(blank=True, null=True)

    class Meta:
        default_related_name = 'profile'


class RetailerMapping(models.Model):
    stockist_id = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='stockist')
    retailer_id = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='retailer')

    class Meta:
        default_related_name = 'retailer_mapping'


class TransactionLog(models.Model):
    issuer_id = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='issuer')
    receiver_id = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='receiver')
    token_amount = models.IntegerField()
    transaction_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        default_related_name = 'transaction_log'


class AvailableToken(models.Model):
    username = models.OneToOneField(User, on_delete=models.DO_NOTHING, primary_key=True)
    token_amount = models.IntegerField()

    class Meta:
        default_related_name = 'available_token'


class TokenPlayLog(models.Model):
    retailer = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    token_amount = models.IntegerField()
    remarks = models.CharField(max_length=255)
    transaction_date = models.DateTimeField(auto_now_add=True)


class GrantedToken(models.Model):
    session = models.CharField(max_length=255, primary_key=True)
    token_amount = models.PositiveIntegerField()


class GameRound(models.Model):
    username = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    session = models.ForeignKey(GrantedToken, on_delete=models.DO_NOTHING)
    tokens_playing_for = models.IntegerField()
    tokens_won = models.IntegerField()
    tokens_remaining = models.IntegerField()
    won_on_number = models.IntegerField(blank=True, null=True)
    is_jackpot = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
