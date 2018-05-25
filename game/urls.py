from django.urls import path

from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.loggedin_check, name='login'),
    path('logout', auth_views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('users/<int:user_id>', views.userPage, name='userPage'),
    path('games/<int:game_id>', views.gamePage, name='gamePage'),
    path('games/new', views.newGame, name='newGame'),
    path('leaderboard', views.leaderboard, name='leaderboard'),

    # these are user taken game actions
    path('games/<int:game_id>/hit', views.gameHit, name="hit"),
    path('games/<int:game_id>/insure', views.gameInsure, name="insure"),
    path('games/<int:game_id>/stand', views.gameStand, name="stand"),
    path('games/<int:game_id>/double', views.gameDouble, name="double"),
    path('games/<int:game_id>/split', views.gameSplit, name="split"),
]
