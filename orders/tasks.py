"""Background tasks for the orders app."""
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_order_confirmation(order_id: int) -> None:
    from .models import Order

    order = Order.objects.select_related("user").get(pk=order_id)
    subject = f"Замовлення #{order.pk} прийнято"
    body = f"Дякую за замовлення! Сумма до сплати: {order.total_price}. Статус: {order.get_status_display()}."

    if order.user.email:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [order.user.email])
    send_mail(
        f"Нове замовлення #{order.pk}",
        f"Користувач {order.user} оформив замовлення на{order.total_price}.",
        settings.DEFAULT_FROM_EMAIL,
        [settings.ADMIN_EMAIL],
    )
