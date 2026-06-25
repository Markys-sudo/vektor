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
        
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255, blank=True)
    address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    city = models.CharField(max_length=100, blank=True)


    def __str__(self):
        return f"{self.user.username}'s Profile"