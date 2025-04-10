# main/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # The username, email, and password fields are inherited from AbstractUser.
    # Add any additional fields needed:
    email_confirmed = models.BooleanField(default=False)
    admin_approved = models.BooleanField(default=False)
