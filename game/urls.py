from django.urls import path

from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', auth_views.login, {'template_name': 'login.html'}, name='login'),
    path('logout', auth_views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('users/<int:user_id>', views.userPage, name='userPage'),
    path('games/<int:game_id>', views.gamePage, name='gamePage'),
]
