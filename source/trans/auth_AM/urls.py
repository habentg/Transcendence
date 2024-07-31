from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('home/', views.home_page, name='home_page'),
    path('signup/', views.signup_page, name='signup_page'),
    path('signin/', views.signin_page, name='signin_page'),
    path('oauth/callback/', views.oauth_callback, name='oauth_callback'),
    path('signout/', views.sign_out, name='signout_page'),
    path('password_reset/', views.password_reset, name='password_reset'),
    path('reset/<uidb64>/<token>/', views.password_reset_newpass, name='password_reset_newpass'),
    # path('password_reset_complete/', views.password_reset_complete, name='password_reset_complete'),
]