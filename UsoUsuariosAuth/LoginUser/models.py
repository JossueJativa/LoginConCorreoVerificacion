from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    #Agregar los campos que necesito
    phone = models.CharField(max_length=10, null=True)
    identity = models.CharField(max_length=10, null=True)
    numverification = models.CharField(max_length=4, null=True)
    is_verified = models.BooleanField(default=False)
