from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django import forms
from .forms import UserRegistrationForm, GameStartForm
from .models import Game

def index(request):
    # the homepage
    return render(request, 'index.html')

def userPage(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    return render(request, 'user.html', {'pageUser': user})

def gamePage(request, game_id):
    # TODO: Check if user signed in. Check if user can access this page

    game = get_object_or_404(Game, pk=game_id)

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

                return HttpResponseRedirect('/games/' + str(gm.id))

        # Create a new game
        return HttpResponseRedirect('/game/' + str(gm.id))
    else:
        # this is a get request to the page to start a game
        # must be logged in to see this
        form = GameStartForm()

    return render(request, 'startGame.html', {'form': form})

# TODO: Use this to ensure logged - in users cannot see the log in form
def loggedin_check(request):
    pass

def register(request):
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

                return HttpResponseRedirect('/')
            else:
                raise forms.ValidationError('Looks like that username is already in use')
    else:
        # render the page with the form to sign up
        form = UserRegistrationForm()

    # only hit this if either of the else cases are hit
    return render(request, 'register.html', {'form' : form})
