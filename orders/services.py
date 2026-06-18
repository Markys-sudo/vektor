
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from django.db import transaction

from products.models import Product

from .exceptions import OutOfStockError
from .models import Order, OrderItem
from .tasks import send_order_confirmation


@dataclass(frozen=True)
class CartLine:
    product_id: int
    quantity: int


@transaction.atomic
def create_order(*, user, lines: list[CartLine], shipping_address: str) -> Order:
    """Create an order atomically from cart lines.

    Locks the involved product rows (``select_for_update``) so concurrent
    checkouts cannot oversell, re-checks stock, snapshots prices into the order
    items, decrements stock, and schedules a confirmation email only after the
    transaction commits.
    """
    if not lines:
        raise ValueError("Cannot create an order with no items.")

    product_ids = [line.product_id for line in lines]
    locked = Product.objects.select_for_update().filter(id__in=product_ids, is_active=True)
    products = {p.id: p for p in locked}

    order = Order.objects.create(
        user=user, shipping_address=shipping_address, status=Order.Status.PENDING
    )

    total = Decimal("0")
    for line in lines:
        product = products.get(line.product_id)
        if product is None:
            raise OutOfStockError(f"Товар {line.product_id} недоступен.")
        if line.quantity > product.stock:
            raise OutOfStockError(f"Недостаточно остатка для «{product.name}».")

        OrderItem.objects.create(
            order=order, product=product, quantity=line.quantity, price=product.price
        )
        product.stock -= line.quantity
        product.save(update_fields=["stock"])
        total += product.price * line.quantity

    order.total_price = total
    order.save(update_fields=["total_price"])

    transaction.on_commit(lambda: send_order_confirmation.delay(order.id))
    return order
