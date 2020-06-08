from django.urls import path
from .views import (
    loginView,
    dashboardView,
    userInfoView,
    createUserView,
    blockUserView,
    grantTokenView,
    transactionLogView,
    retailerProfileView,
    gameConsoleView,
    logoutView
)


urlpatterns = [
    path('', loginView, name='login'),
    path('dashboard', dashboardView, name='dashboard'),
    path('userinfo', userInfoView, name='userinfo'),
    path('create/<str:category>', createUserView, name='create'),
    path('blockuser', blockUserView, name='blockuser'),
    path('granttoken', grantTokenView, name='granttoken'),
    path('transactionlog', transactionLogView, name='transactionlog'),
    path('rtlprofile', retailerProfileView, name='rtlprofile'),
    path('gameconsole', gameConsoleView, name='gameconsole'),
    path('logout', logoutView, name='logout')
]
