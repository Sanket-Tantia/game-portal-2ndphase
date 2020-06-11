from django.shortcuts import render, redirect

# authentication
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from .decorators import isathenticated_user, authorized_user

# messages
from django.contrib import messages

# redirect after form submit
from django.http import HttpResponseRedirect

# query functions
from django.db.models import Count, Q, Sum

# forms
from .forms import  (
    CreateUserForm,
    CreateProfileForm,
    RetailerMappingForm,
    TransactionLogForm,
    AvailableTokenForm,
    TokenPlayLogForm,
    GrantedTokenForm
)

# models
from .models import (
    Profile,
    RetailerMapping,
    TransactionLog,
    AvailableToken,
    TokenPlayLog,
    GrantedToken,
    GameRound
)

# default libs
from datetime import datetime
from collections import defaultdict
import json

# Create your views here.
@isathenticated_user
def loginView(request):
    context = {}

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None:
            login(request, user)
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
                if group == 'admin':
                    return redirect('dashboard')
                elif group == 'stockist':
                    return redirect('userinfo')
                else:
                    return redirect('gameconsole')
        else:
            messages.info(request, 'Username or password is incorrect')

    return render(request, 'deskapp/login.html', context)


@login_required(login_url='login')
@authorized_user(allowed_roles=['admin'])
def dashboardView(request):
    context = {}

    context['total_act_stockist'] = User.objects.filter(groups__name='stockist', is_active=1).count()
    context['total_act_retailer'] = User.objects.filter(groups__name='retailer', is_active=1).count()
    context['total_blk_stockist'] = User.objects.filter(groups__name='stockist', is_active=0).count()
    context['total_blk_retailer'] = User.objects.filter(groups__name='retailer', is_active=0).count()

    return render(request, 'deskapp/dashboard.html', context)


@login_required(login_url='login')
def logoutView(request):
    if request.user.groups.all()[0].name == 'retailer':
        try:
            granted_token = GrantedToken.objects.get(pk=request.session._session_key).token_amount
        except GrantedToken.DoesNotExist:
            granted_token = 0

        if granted_token>0:
            token_play_log_form = TokenPlayLogForm({
                'retailer': request.user.id,
                'token_amount': -granted_token,
                'remarks': "Credited remaining granted tokens to available tokens when log out"
            })
            if token_play_log_form.is_valid():
                token_play_log_form.save()
            else:
                print("Token play log form is not valid", token_play_log_form.erros)

            retailer_token_obj = AvailableToken.objects.get(pk=request.user.id)
            retailer_token_obj.token_amount += granted_token
            retailer_token_obj.save()

    logout(request)
    return redirect('login')


@login_required(login_url='login')
@authorized_user(allowed_roles=['admin','stockist'])
def createUserView(request, category):
    context = {}
    if request.user.groups.all()[0].name == 'admin' and category.lower() == 'retailer':
        context['allstockists'] = [i.username for i in User.objects.filter(groups__name='stockist')]
    elif request.user.groups.all()[0].name == 'stockist':
        # category will be all set to retailer for stockist in case user tries to change url params
        category = 'retailer'

    if request.method == 'POST':
        # print(request.POST)
        try:
            user_form = CreateUserForm({
                'username': request.POST.get('username'),
                'email': request.POST.get('email'),
                'password1': request.POST.get('password1'),
                'password2': request.POST.get('password2')
            })
            if user_form.is_valid():
                # adding data to auth_user default table
                username = user_form.cleaned_data.get('username')
                created_user = user_form.save()
                group = Group.objects.get(name=category)
                created_user.groups.add(group)
                
                # adding data to profile for the created user
                profile_form = CreateProfileForm({
                    'username': created_user.id,
                    'fullname': request.POST.get('fullname'),
                    'phone': request.POST.get('phone'),
                    'city': request.POST.get('city'),
                    'state': request.POST.get('state'),
                })

                if profile_form.is_valid():
                    # saving data to database
                    profile_form.save()

                    # saving that user details in available token table
                    available_token_form = AvailableTokenForm({
                        'username': created_user.id,
                        'token_amount': 0
                    })

                    if available_token_form.is_valid():
                        available_token_form.save()
                    else:
                        print("Available Token form not valid", available_token_form.errors)


                    if category.lower() == 'retailer':
                        if request.user.groups.all()[0].name == 'admin':
                            # get stockist username from post body
                            stockist_id = User.objects.get(username=request.POST.get('stockistusername')).id
                        else:
                            # get logged in user id
                            stockist_id = request.user.id

                        retailer_mapping_form = RetailerMappingForm({
                            'stockist_id': stockist_id,
                            'retailer_id': created_user.id,
                        })

                        if retailer_mapping_form.is_valid():
                            retailer_mapping_form.save()
                            return redirect('dashboard')
                        else:
                            print("Retailer mapping form is invalid", retailer_mapping_form.errors)
                    else:
                        return redirect('dashboard')

                else:
                    # delete that user from default auth_user table to avoid mismatch
                    User.objects.get(username=username).delete()
                    print("Profile form not valid", profile_form.errors)

            else:
                print("User form not valid", user_form.errors)
        except Exception as e:
            print(e)

    context['category'] = category
    return render(request, 'deskapp/create_user.html', context)


@login_required(login_url='login')
@authorized_user(allowed_roles=['admin','stockist'])
def userInfoView(request):
    context = {}

    if request.user.groups.all()[0].name == 'admin':
        queryset = Profile.objects.select_related('username').all()
    else:
        myretailers = [i.retailer_id.id for i in RetailerMapping.objects.select_related('retailer_id').filter(stockist_id=request.user.id)]
        queryset = Profile.objects.select_related('username').filter(username__id__in=myretailers)

    all_users = []
    for user in queryset:
        all_users.append({
            'username': user.username.username,
            'fullname': user.fullname,
            'email':user.username.email,
            'category': user.username.groups.all()[0].name,
            'balance': AvailableToken.objects.get(pk=user.username.id).token_amount,
            'winx': user.winx if user.winx else '--',
            'probability': f"{user.probability}%" if user.probability else '--',
            'last_login': user.username.last_login.strftime("%b %d, %Y") if user.username.last_login else None,
            'status': 'Blocked' if user.username.is_active == 0 else "Active",
            'date_joined': user.username.date_joined.strftime("%b %d, %Y"),
            'phone': user.phone,
            'city': user.city,
            'state': user.state
        })

    context['all_users'] = all_users
    

    return render(request, 'deskapp/user_info.html', context)


@login_required(login_url='login')
@authorized_user(allowed_roles=['admin','stockist'])
def blockUserView(request):
    context = {}

    if request.method == 'POST':

        if request.user.groups.all()[0].name == 'admin' and request.POST.get('usertype').lower() == 'stockist':
            # blocking stockist
            user = User.objects.get(username=request.POST.get('stockistusername'))
        else:
            # blocking retailer
            user = User.objects.get(username=request.POST.get('retailerusername'))
        
        user.is_active=request.POST.get('status')
        user.save()

        return HttpResponseRedirect('blockuser')

            

    if request.user.groups.all()[0].name == 'admin':
        context['allstockists'] = [i.username for i in User.objects.filter(groups__name='stockist')]
        context['allretailers'] = [i.username for i in User.objects.filter(groups__name='retailer')]
    else:
        queryset = RetailerMapping.objects.select_related('retailer_id').filter(stockist_id=request.user.id)
        context['allretailers'] = [i.retailer_id.username for i in queryset]

    return render(request, 'deskapp/block_user.html', context)


@login_required(login_url='login')
@authorized_user(allowed_roles=['admin','stockist'])
def grantTokenView(request):
    context = {}

    if request.method == 'POST':
        # granting tokens to stockist
        if request.user.groups.all()[0].name == 'admin' and request.POST.get('usertype').lower() == 'stockist':
            receiver_id = User.objects.get(username=request.POST.get('stockistusername')).id
        # granting tokens to retailer
        else:
            receiver_id = User.objects.get(username=request.POST.get('retailerusername')).id

        token_amount = int(request.POST.get('token_amount'))
        current_token_amount = int(request.POST.get('current_token_amount'))
        
        # in case the issuer is a stockist then subtract the tokens from him
        if request.user.groups.all()[0].name == 'stockist':
            my_tokens_amount = int(request.POST.get('my_tokens_amount'))
            if my_tokens_amount < token_amount:
                print("Issuing more than available tokens")
                return HttpResponseRedirect('granttoken')

            stockist_token_obj = AvailableToken.objects.get(pk=request.user.id)
            stockist_token_obj.token_amount = my_tokens_amount - token_amount
            stockist_token_obj.save()

        transaction_log_form = TransactionLogForm({
                'issuer_id': request.user.id,
                'receiver_id': receiver_id,
                'token_amount': token_amount
        })

        if transaction_log_form.is_valid():
            transaction_log_form.save()

            user_token_obj = AvailableToken.objects.get(pk=receiver_id)
            user_token_obj.token_amount = current_token_amount + token_amount
            user_token_obj.save()

        else:
            print("Token transaction form is not valid", transaction_log_form.errors)
        return HttpResponseRedirect('granttoken')


    if request.user.groups.all()[0].name == 'admin':
        context['allstockists'] = dict((i.username.username, i.token_amount) for i in AvailableToken.objects.select_related('username').filter(username__groups__name='stockist'))
        context['allretailers'] = dict((i.username.username, i.token_amount) for i in AvailableToken.objects.select_related('username').filter(username__groups__name='retailer'))
    else:
        myretailers = [i.retailer_id.id for i in RetailerMapping.objects.select_related('retailer_id').filter(stockist_id=request.user.id)]
        context['allretailers'] = dict((i.username.username, i.token_amount) for i in AvailableToken.objects.select_related('username').filter(username__id__in=myretailers))
        context['stockist_token'] = AvailableToken.objects.get(pk=request.user.id).token_amount

    return render(request, 'deskapp/grant_token.html', context)


@login_required(login_url='login')
@authorized_user(allowed_roles=['admin','stockist','retailer'])
def transactionLogView(request):
    context = {}

    if request.user.groups.all()[0].name == 'admin':
        queryset_stockist = TransactionLog.objects.select_related('receiver_id').filter(receiver_id__groups__name='stockist').order_by('-transaction_date')
        queryset_retailer = TransactionLog.objects.select_related('receiver_id').filter(receiver_id__groups__name='retailer').order_by('-transaction_date')
        queryset_play = TokenPlayLog.objects.select_related('retailer').order_by('-transaction_date')

    elif request.user.groups.all()[0].name == 'stockist':
        myretailers = [i.retailer_id.id for i in RetailerMapping.objects.select_related('retailer_id').filter(stockist_id=request.user.id)]
        queryset_stockist = TransactionLog.objects.filter(receiver_id=request.user.id).order_by('-transaction_date')
        queryset_retailer = TransactionLog.objects.filter(receiver_id__in=myretailers).order_by('-transaction_date')
        queryset_play = TokenPlayLog.objects.select_related('retailer').order_by('-transaction_date').filter(retailer__in=myretailers)

    else:
        queryset_retailer = TransactionLog.objects.filter(receiver_id=request.user.id).order_by('-transaction_date')
        queryset_play = TokenPlayLog.objects.select_related('retailer').order_by('-transaction_date').filter(retailer=request.user.id)

    all_transactions_stockist, all_transactions_retailes, allplaytokens = [], [], []

    if request.user.groups.all()[0].name == 'admin' or request.user.groups.all()[0].name == 'stockist':
        # all stockist for admin or only stockist personal
        for transaction in queryset_stockist:
            all_transactions_stockist.append({
                'issuer': transaction.issuer_id.username,
                'issuer_type': transaction.issuer_id.groups.all()[0].name,
                'receiver': transaction.receiver_id.username,
                'receiver_type': transaction.receiver_id.groups.all()[0].name,
                'token_amount': transaction.token_amount,
                'transaction_date': transaction.transaction_date.strftime("%b %d, %Y")
            })

    # all retailers for admin or only stockist retailers or retailer personal
    for transaction in queryset_retailer:
        all_transactions_retailes.append({
            'issuer': transaction.issuer_id.username,
            'issuer_type': transaction.issuer_id.groups.all()[0].name,
            'receiver': transaction.receiver_id.username,
            'receiver_type': transaction.receiver_id.groups.all()[0].name,
            'token_amount': transaction.token_amount,
            'transaction_date': transaction.transaction_date.strftime("%b %d, %Y")
        })

    # all retailers play for admin or only stockist retailers play or retailer play personal
    for pt in queryset_play:
        allplaytokens.append({
            'retailer': pt.retailer.username,
            'token_amount': pt.token_amount,
            'remarks': pt.remarks,
            'transaction_date': pt.transaction_date.strftime("%b %d, %Y")
        })
        

    context['all_transactions_stockist'] = all_transactions_stockist
    context['all_transactions_retailes'] = all_transactions_retailes
    context['allplaytokens'] = allplaytokens
    try:
        context['granted_token'] = GrantedToken.objects.get(pk=request.session._session_key).token_amount
    except GrantedToken.DoesNotExist:
        context['granted_token'] = 0

    return render(request, 'deskapp/transaction_log.html', context)


@login_required(login_url='login')
@authorized_user(allowed_roles=['admin'])
def retailerProfileView(request):
    context = {}

    if request.method == 'POST':
        print(request.POST)

        profile_obj = Profile.objects.get(
            username=User.objects.get(username=request.POST.get('retailerusername')).id
        )

        profile_obj.probability = request.POST.get('probability')
        profile_obj.winx = request.POST.get('winx')

        profile_obj.save()

        return HttpResponseRedirect('rtlprofile')


    queryset = RetailerMapping.objects.all()
    stockist_retailer_mappping = defaultdict(list)

    for obj in queryset:
        stockist_retailer_mappping[obj.stockist_id.username].append(obj.retailer_id.username)

    context['stockist_retailer_mappping'] = dict(stockist_retailer_mappping)

    return render(request, 'deskapp/retailer_profile.html', context)


@login_required(login_url='login')
@authorized_user(allowed_roles=['retailer'])
def gameConsoleView(request):
    context = {}

    if request.method == 'POST':
        # print(request.POST)

        # deducting available token
        my_tokens_amount = int(request.POST.get('my_tokens_amount'))
        token_amount = int(request.POST.get('token_amount'))
        if my_tokens_amount < token_amount:
            print("Issuing more than available tokens")
            return HttpResponseRedirect('gameconsole')

        retailer_token_obj = AvailableToken.objects.get(pk=request.user.id)
        retailer_token_obj.token_amount = my_tokens_amount - token_amount
        retailer_token_obj.save()

        token_play_log_form = TokenPlayLogForm({
            'retailer': request.user.id,
            'token_amount': request.POST.get('token_amount'),
            'remarks': "Tokens granted from the website portal"
        })
        if token_play_log_form.is_valid():
            token_play_log_form.save()
        else:
            print("Token play log form is not valid", token_play_log_form.erros)

        granted_token_form = GrantedTokenForm({
            'session': request.session._session_key,
            'token_amount': request.POST.get('token_amount')
        })

        if granted_token_form.is_valid():
            granted_token_form.save()
        else:
            print("Granted Token form not valid", granted_token_form.errors)
        
        return HttpResponseRedirect('gameconsole')

    try:
        available_tokens = AvailableToken.objects.get(pk=request.user.id).token_amount
    except AvailableToken.DoesNotExist:
        available_tokens = 0

    context['available_tokens'] = available_tokens
    try:
        context['granted_token'] = GrantedToken.objects.get(pk=request.session._session_key).token_amount
    except GrantedToken.DoesNotExist:
        context['granted_token'] = 0

    return render(request, 'deskapp/game_console.html', context)

@login_required(login_url='login')
@authorized_user(allowed_roles=['admin','stockist'])
def gameResultView(request):
    context = {}

    # queryset = GameRound.objects.all().order_by('username')
    retailers_game_history = {}
    if request.user.groups.all()[0].name == 'admin':
        queryset = GameRound.objects.values('username').annotate(
            gamesplayed=Count('pk'),
            gameswon=Count('pk', filter=Q(tokens_won__gt=0)),
            tokenswon=Sum('tokens_won', filter=Q(tokens_won__gt=0))
        )
    else:
        myretailers = [i.retailer_id.id for i in RetailerMapping.objects.filter(stockist_id=request.user.id)]
        queryset = GameRound.objects.values('username').filter(username__in=myretailers).annotate(
            gamesplayed=Count('pk'),
            gameswon=Count('pk', filter=Q(tokens_won__gt=0)),
            tokenswon=Sum('tokens_won', filter=Q(tokens_won__gt=0))
        )

    for row in queryset:
        user_id = row['username']
        username = User.objects.get(pk=user_id).username
        row['balance'] = AvailableToken.objects.get(pk=user_id).token_amount
        row['margin'] = "{:.2f}%".format(100*row['gameswon']/row['gamesplayed'])

        retailers_game_history[username] = row

    context['retailers_game_history'] = retailers_game_history

    return render(request, 'deskapp/game_result.html', context)


@login_required(login_url='login')
@authorized_user(allowed_roles=['admin','stockist','retailer'])
def gameEarningView(request):
    context = {}

    all_game_earning = []

    if request.user.groups.all()[0].name == 'admin':
        queryset = GameRound.objects.all()
    elif request.user.groups.all()[0].name == 'stockist':
        myretailers = [i.retailer_id.id for i in RetailerMapping.objects.filter(stockist_id=request.user.id)]
        queryset = GameRound.objects.filter(username__in=myretailers)
    else:
        queryset = GameRound.objects.filter(username=request.user.id)

    for each_game in queryset:
        all_game_earning.append({
            'username': each_game.username.username,
            'tokens_playing_for': each_game.tokens_playing_for,
            'tokens_won': each_game.tokens_won,
            'tokens_remaining': each_game.tokens_remaining,
            'won_on_number': each_game.won_on_number,
            'is_jackpot': each_game.is_jackpot,
            'transaction_date': each_game.created_date.strftime("%b %d, %Y"),
            'commission': each_game.tokens_playing_for * 0.05,
            'net_pay': each_game.tokens_playing_for * .95 - each_game.tokens_won
        })
    context['all_game_earning'] = all_game_earning

    try:
        context['granted_token'] = GrantedToken.objects.get(pk=request.session._session_key).token_amount
    except GrantedToken.DoesNotExist:
        context['granted_token'] = 0

    return render(request, 'deskapp/game_earning.html', context)


# TASKS LEFT
# success form message
# admin dashboard