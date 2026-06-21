from orders.models import OrderItem, Order


def has_purchased(user, product):
    if not user.is_authenticated:
        return False

    return OrderItem.objects.filter(
        order__user=user,
        order__status=Order.Status.PAID,   # або DELIVERED (краще)
        product=product
    ).exists()