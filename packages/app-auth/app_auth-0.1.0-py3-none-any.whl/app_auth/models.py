from django.db import models
from django.contrib.auth.models import AbstractUser

AUTH_USER_MODEL = "yourapp.CustomUser"

class CustomUser(AbstractUser):

    email = models.EmailField(unique=True)
    name =models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    sub = models.CharField(max_length=255, unique=True, blank=True, null=True)
    surname = models.CharField(max_length=200, blank=True, null=True)  
    given_name = models.CharField(max_length=200, blank=True, null=True)  
    preferred_username = models.CharField(max_length=200, blank=True, null=True)  
    nickname = models.CharField(max_length=200, blank=True, null=True)  
    email_verified = models.BooleanField(default=False)
    nonce = models.CharField(max_length=255, blank=True, null=True)


    def __str__(self):
        return self.email

    
