from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import Player
import requests
import os

# Create your views here.
def home_page(request):
    if request.user.is_authenticated:  # User is logged in, show the home page
        return render(request, 'auth_AM/home.html', context={})
    else:  # User is not logged in, show the landing page
        return render(request, 'auth_AM/landing.html', context={})

def signup_page(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        # now we need to creat a user with this information
        if Player.objects.filter(username=username).exists():
            print("username exists")
            messages.info(request, "Username already taken!")
            return redirect('/signup/')

        player = Player.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email
        )
        player.set_password(password)
        player.save()
        """ 
            # gonna login the user,
            # hide the signup/signin buttons and put an avatar of the user (gonna add it as a file to the db)
        """
        login(request, player)
        return redirect('/home/')
    client_id = os.getenv('CLIENT_ID')
    return render(request, 'auth_AM/signup.html', {'client_id': client_id})



def signin_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not Player.objects.filter(username=username).filter():
            messages.error(request, "Username not found!")
            return redirect('/signin/')
        
        player = authenticate(request, username=username, password=password)
        if player is None:
            messages.error(request, "Invalid password!")
            return redirect('/signin/')
        login(request, player)
        return redirect('/home/')

    client_id = os.getenv('CLIENT_ID')
    return render(request, 'auth_AM/signin.html', {'client_id': client_id})



def oauth_callback(request):
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    code = request.GET.get('code')
    if not code:
        return HttpResponse('Authorization failed.')
    # Exchange authorization code for access token
    token_response = requests.post('https://api.intra.42.fr/oauth/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://localhost/oauth/callback/',
        'client_id': client_id,
        'client_secret': client_secret,
    })

    if token_response.status_code != 200:
        return HttpResponse('Failed to obtain access token.')

    token_json = token_response.json()
    access_token = token_json.get('access_token')

    if not access_token:
        return HttpResponse('Failed to obtain access token.')

    # Use the access token to access the user's data
    user_info_response = requests.get('https://api.intra.42.fr/v2/me', headers={
        'Authorization': f'Bearer {access_token}'
    })

    if user_info_response.status_code != 200:
        return HttpResponse('Failed to obtain user information.')
    print(user_info_response)
    user_info = user_info_response.json()
    """ checking if user already exists in a db """
    player = Player.objects.filter(username=user_info['login']).first()
    if player:
        print("42 username exists")
        login(request, player)
        return redirect('/home/')
    
    """ creating new player and saving him in db """
    newPlayer = Player.objects.create_user(
        first_name=user_info['first_name'],
        last_name=user_info['last_name'],
        username=user_info['login'],
        email=user_info['email']
    )
    # player.set_password(password)
    # newPlayer.save()
    login(request, newPlayer)
    return redirect('/home/')
    # return render(request, 'auth_AM/auth_failed.html', {'user_info': user_info})
    # return HttpResponse(f'Hello, {user_info["first_name"]}')

def authorized(request):
    return HttpResponse("authorized!!!")