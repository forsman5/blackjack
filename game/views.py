from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django import forms
from .forms import UserRegistrationForm

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

def newGame(request):
    # Create a new game
    return HttpResponseRedirect('/game/' )#+ game.id)

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
