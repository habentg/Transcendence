import requests
import os
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import Player
from django.core.mail import send_mail
from django.conf import settings
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode

# Create your views here.
def home_page(request):
    if not request.user.is_authenticated: # User is not logged in, show the landing page
        return render(request, 'auth_AM/landing.html', context={})
    else:  
        player = request.user
        context = {
            'Fullname': player.get_full_name(),
            'Username': player.username,
            'Email': player.email,
            'is_authenticated': player.is_authenticated,
        }
        return render(request, 'auth_AM/home.html', {'context': context})

def signup_page(request):
    if request.method == 'GET':
        client_id = os.getenv('CLIENT_ID')
        return render(request, 'auth_AM/signup.html', {'client_id': client_id})
    elif request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        # now we need to creat a user with this information
        if Player.objects.filter(username=username.lower()).exists():
            print("username exists")
            messages.info(request, "Username already taken!")
            return redirect('/signup/')
    # Doc: https://docs.djangoproject.com/en/5.0/ref/contrib/auth/#django.contrib.auth.models.UserManager.create_user
        player = Player.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username.lower(),
            email=email
        )
        player.set_password(password)
        player.save()
        """ 
            # gonna login the user,
            # hide the signup/signin buttons and put an avatar of the user (gonna add it as a file to the db)
        """
        messages.success(request,f'Welcome to PingPong, {player.username}!')
        login(request, player)
        return redirect('/home/')



def signin_page(request):
    if request.method == 'GET':
        client_id = os.getenv('CLIENT_ID')
        return render(request, 'auth_AM/signin.html', {'client_id': client_id})
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not Player.objects.filter(username=username.lower()).filter():
            messages.error(request, "Username not found!")
            return redirect('/signin/')
        
        player = authenticate(request, username=username, password=password)
        if player is None:
            messages.error(request, "Invalid password!")
            return redirect('/signin/')
        login(request, player)
        messages.success(request,f'Hi {username}, welcome back!')
        return redirect('/home/')

def sign_out(request):
    logout(request)
    # messages.success(f'Thank you for playing, {request.user.username}')
    return redirect('/home/')

""" 
    Steps of our callback function after Oauth.
    1. geting the client id and secret from our .env file
    2. checking for autherization code after signing up to 42.
    3. ask 42/oauth/token for access token using our code.
    4. then just get the user information using the access token
"""
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
    user_info = user_info_response.json()
    """ checking if user already exists in a db """
    player = Player.objects.filter(username=user_info['login']).first()
    if player:
        print("42 username exists")
        login(request, player)
        messages.success(request,f'Hi {player.username}, welcome back!')
        return redirect('/home/')
    
    """ creating new player and saving him in db """
    # Doc: https://docs.djangoproject.com/en/5.0/ref/contrib/auth/#django.contrib.auth.models.UserManager.create_user
    newPlayer = Player.objects.create_user(
        first_name=user_info['first_name'],
        last_name=user_info['last_name'],
        username=user_info['login'],
        email=user_info['email']
    )
    # If no password is provided, set_unusable_password() will be called.
    login(request, newPlayer)
    messages.success(request,f'Welcome to PingPong, {newPlayer.username}!')
    return redirect('/home/')


""" Sending password reset link by email """

def password_reset_newpass(request, uidb64=None, token=None):
    Player = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        player = Player.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Player.DoesNotExist):
        player = None

    if player is not None and default_token_generator.check_token(player, token):
        if request.method == 'POST':
            if player.password_reset_token!= token:
                messages.error(request, 'The reset password link is no longer valid.')
                return redirect('/password_reset/')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            if new_password != confirm_password:
                messages.error(request, 'Passwords do not match.')
                return render(request, 'auth_AM/password_reset_newpass.html', context={})
            player.set_password(new_password)
            player.save()
            messages.success(request, 'Your password has been set. You can now log in.')
            return redirect('/signin/')
        else:
            return render(request, 'auth_AM/password_reset_newpass.html', context={})
    else:
        messages.error(request, 'The reset password link is no longer valid.')
        return redirect('password_reset')

# def password_reset_complete(request):

def emailing_password_reset_link(request, reseting_player, to_email):
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [to_email]
    subject = "Password Reset Requested"
    email_template_name = "auth_AM/password_reset_email_tamplate.txt"
    c = {
        'email': reseting_player.email,
        'domain': 'localhost',
        'site_name': 'Your Site',
        'uid': urlsafe_base64_encode(force_bytes(reseting_player.pk)),
        'user': reseting_player,
        'token': default_token_generator.make_token(reseting_player),
        'protocol': 'http',
    }
    # to prevent players reseting thier password using older token
    reseting_player.password_reset_token = c['token']
    reseting_player.save()
    email_body = render_to_string(email_template_name, c)
    send_mail(subject, email_body, from_email, recipient_list, fail_silently=False)

def password_reset(request):
    if request.method == 'GET':
        return render(request, 'auth_AM/password_reset.html', context={})
    elif request.method == 'POST':
        to_email = request.POST.get('email')
        Player = get_user_model()
        reseting_player = Player.objects.filter(email=to_email).first()
        if reseting_player is None:
            messages.error(request, "Email not found in our db!")
            return redirect('/password_reset/')
        emailing_password_reset_link(request, reseting_player, to_email)
        return render(request, 'auth_AM/password_reset_complete.html', context={})
