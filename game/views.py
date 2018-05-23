from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django import forms
from .forms import UserRegistrationForm, GameStartForm
from .models import Game

def index(request):
    # the homepage
    return render(request, 'index.html')

def userPage(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    return render(request, 'user.html', {'pageUser': user})

@login_required(login_url='login')
def gamePage(request, game_id):
    game = get_object_or_404(Game, pk=game_id)

    if game.user != request.user:
        # this is not the user's game
        # TODO: notify the user that he cannot access that page
        return HttpResponseRedirect(reverse_lazy('user', args=(request.user.id,)))

    return render(request, 'game.html', {'game': game})

@login_required(login_url='login')
def newGame(request):
    if request.method == 'POST':
        form = GameStartForm(request.POST)
        if (form.is_valid()):
            bet = form.cleaned_data['bet']

            if bet > request.user.profile.money:
                # can't afford this game
                raise forms.ValidationError('You don\'t have that much money in your account!')
            else:
                # this is requesting a new game is started, with parameters
                gm = Game.create(user = request.user, bet = bet)

                return HttpResponseRedirect(reverse_lazy('gamePage', args=(gm.id,)))
    else:
        # this is a get request to the page to start a game
        # must be logged in to see this
        form = GameStartForm()

    return render(request, 'startGame.html', {'form': form})

# This is used to ensure that logged in users cannot see this page
def loggedin_check(request):
    if request.user != None and request.user.is_authenticated:
        # TODO: notify the user that he cannot access that page when logged in
        return HttpResponseRedirect(reverse_lazy('index'))
    else:
        return auth_views.login(request, template_name='login.html')

def register(request):
    # ensure that logged in users cannot see this page
    if request.user != None and request.user.is_authenticated:
        # TODO: notify the user that he cannot access that page when logged in
        return HttpResponseRedirect(reverse_lazy('index'))

    if request.method == 'POST':
        # create and save a new username
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            userObj = form.cleaned_data
            username = userObj['username']
            email =  userObj['email']
            password =  userObj['password']

            if not (User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists()):
                User.objects.create_user(username, email, password)

                user = authenticate(username = username, password = password)

                login(request, user)

                return HttpResponseRedirect(reverse_lazy('index'))
            else:
                raise forms.ValidationError('Looks like that username is already in use')
    else:
        # render the page with the form to sign up
        form = UserRegistrationForm()

    # only hit this if either of the else cases are hit
    return render(request, 'register.html', {'form' : form})
