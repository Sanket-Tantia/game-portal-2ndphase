from django.urls import path
from .views import GameRoundCreateView, GameRoundListView, UserGameProfileView, UserRefillTokenView, UserAuthorizeRefillView

urlpatterns = [
    path('gameround/create/', GameRoundCreateView.as_view(), name='gameround-create'),
    path('gameround/<str:session>/', GameRoundListView.as_view(), name='gameround-detail'),
    path('gameinfo/', UserGameProfileView.as_view(), name='user-gameprofile'),
    path('refill/', UserRefillTokenView.as_view(), name='user-refill'),
    path('authorize/', UserAuthorizeRefillView.as_view(), name='user-authorize'),
]
