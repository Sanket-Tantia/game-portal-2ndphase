from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from .models import (
    Profile,
    RetailerMapping,
    TransactionLog,
    AvailableToken,
    TokenPlayLog,
    GrantedToken
)

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class CreateProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['username', 'fullname', 'phone', 'city', 'state']


class RetailerMappingForm(forms.ModelForm):
    class Meta:
        model = RetailerMapping
        fields = ['stockist_id', 'retailer_id']


class TransactionLogForm(forms.ModelForm):
    class Meta:
        model = TransactionLog
        fields = ['issuer_id', 'receiver_id', 'token_amount']


class AvailableTokenForm(forms.ModelForm):
    class Meta:
        model = AvailableToken
        fields = ['username', 'token_amount']


class TokenPlayLogForm(forms.ModelForm):
    class Meta:
        model = TokenPlayLog
        fields = ['retailer', 'token_amount']


class GrantedTokenForm(forms.ModelForm):
    class Meta:
        model = GrantedToken
        fields = ['session', 'token_amount']
