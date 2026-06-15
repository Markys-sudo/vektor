"""Order and order-item models."""
from django.conf import settings
from django.db import models

from products.models import Product, TimeStampedModel


class Order(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Очікується оплата"
        PAID = "paid", "Оплачено"
        SHIPPED = "shipped", "Відправлено"
        DELIVERED = "delivered", "Доставлено"
        CANCELLED = "cancelled", "Відмінено"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_address = models.TextField()

    class Meta:
        indexes = [
            models.Index(fields=["user", "status"], name="order_user_status_idx"),
            models.Index(fields=["user", "-created_at"], name="order_user_created_idx"),
            models.Index(fields=["status", "created_at"], name="order_status_created_idx"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(total_price__gte=0), name="order_total_non_negative"
            ),
        ]

    def __str__(self) -> str:
        return f"Заказ #{self.pk} ({self.get_status_display()})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot at purchase time

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["order", "product"], name="uniq_order_product"),
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0), name="orderitem_quantity_positive"
            ),
            models.CheckConstraint(
                condition=models.Q(price__gte=0), name="orderitem_price_non_negative"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.quantity} × {self.product.name}"

    @property
    def subtotal(self):
        return self.price * self.quantity
