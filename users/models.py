from django.db import models
from orders.models import Order, OrderItem
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)
    telegram_username = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)

    def has_bought(self, product):
        return OrderItem.objects.filter(
            order__user=self, order__status=Order.Status.DELIVERED, product=product
        ).exists()

    def __str__(self):
        return self.username
