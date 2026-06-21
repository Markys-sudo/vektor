from django.db import models
from orders.models import Order,OrderItem
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    telegram_id = models.BigIntegerField(
        null=True,
        blank=True,
        unique=True
    )
    telegram_username = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    
    def has_bought(self, product):
        return OrderItem.objects.filter(
                order__user=self,
                order__status=Order.Status.DELIVERED,
                product=product
            ).exists()