from __future__ import annotations

from decimal import Decimal

from products.models import Product

CART_SESSION_KEY = "cart"


class Cart:

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if cart is None:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart = cart

    def add(self, product, quantity=1, *, replace=False):
        pid = str(product.id)
        current = self.cart.get(pid, 0)
        new_qty = quantity if replace else current + quantity
        self.cart[pid] = max(1, min(new_qty, product.stock))
        self.save()

    def set_quantity(self, product, quantity):
        if quantity <= 0:
            self.remove(product)
        else:
            self.add(product, quantity, replace=True)

    def remove(self, product):
        self.cart.pop(str(product.id), None)
        self.save()

    def clear(self):
        self.session.pop(CART_SESSION_KEY, None)
        self.save()

    def save(self):
        self.session[CART_SESSION_KEY] = self.cart
        self.session.modified = True 

    def __iter__(self):
        products = Product.objects.filter(id__in=self.cart.keys())
        for product in products:
            qty = self.cart[str(product.id)]
            yield {"product": product, "quantity": qty, "subtotal": product.price * qty}

    def __len__(self):
        return sum(self.cart.values())

    @property
    def total(self) -> Decimal:
        products = Product.objects.filter(id__in=self.cart.keys())
        return sum((p.price * self.cart[str(p.id)] for p in products), Decimal("0"))
