from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('home/', views.home_page, name='home_page'),
    path('signup/', views.signup_page, name='signup_page'),
    path('signin/', views.signin_page, name='signin_page'),
]