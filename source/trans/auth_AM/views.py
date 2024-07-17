from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Player

# Create your views here.
def home_page(request):
    return render(request, 'auth_AM/home.html', context={})

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
         
    return render(request, 'auth_AM/signup.html', context={})

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

    return render(request, 'auth_AM/signin.html', context={})