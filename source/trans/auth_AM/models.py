from django.contrib.auth.models import AbstractUser
from django.db import models

class Player(AbstractUser):
    username = models.CharField(max_length=25, unique=True)
    email = models.EmailField()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    def __str__(self):
        return self.username