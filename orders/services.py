from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import Decimal

from django.db import transaction

from products.models import Product
from users.models import User

from .exceptions import OutOfStockError
from .models import Order, OrderItem
from .tasks import send_order_confirmation

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CartLine:
    product_id: int
    quantity: int


@transaction.atomic
def create_order(*, user: User, lines: list[CartLine], shipping_address: str) -> Order:
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
            logger.warning(
                "oversell_blocked product=%s requested=%s available=%s",
                product.id,
                line.quantity,
                product.stock,
            )
            raise OutOfStockError(f"Недостатньо остатку для «{product.name}».")

        OrderItem.objects.create(
            order=order, product=product, quantity=line.quantity, price=product.price
        )
        product.stock -= line.quantity
        product.save(update_fields=["stock"])
        total += product.price * line.quantity

    order.total_price = total
    order.save(update_fields=["total_price"])
    logger.info(
        "order_created id=%s user=%s items=%s total=%s", order.pk, user.pk, len(lines), total
    )

    transaction.on_commit(lambda: send_order_confirmation.delay(order.id))
    return order

@transaction.atomic
def mark_paid(order: Order) -> Order:
    order = Order.objects.select_for_update().get(pk=order.pk)
    """Mock payment success: flip a pending order to paid."""
    if order.status == Order.Status.PENDING:
        order.status = Order.Status.PAID
        order.save(update_fields=["status"])
        logger.info("order_paid id=%s", order.pk)
    return order
