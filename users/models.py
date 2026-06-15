from django.db import models

from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    telegram_id = models.BigIntegerField(
        null=True,
        blank=True,
        unique=True
    )
    telegram_username = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)